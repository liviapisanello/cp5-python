import re
import scrapy
from datetime import datetime, timezone
from games.items import TechTudoJogosSpiderItem

# TechTudo's listing page (/jogos/) is a SPA and doesn't serve static HTML.
# We use the Globo/Bastian internal search API to retrieve article URLs,
# then scrape individual article pages which do serve static HTML.
SEARCH_API = (
    "https://busca.techtudo.com.br/api/site/techtudo.com.br/secoes/jogos"
)
PAGE_SIZE = 20


class TechTudoJogosSpider(scrapy.Spider):
    name = "TechTudoJogos"
    allowed_domains = ["techtudo.com.br", "busca.techtudo.com.br"]

    def start_requests(self):
        yield scrapy.Request(
            url=f"{SEARCH_API}?size={PAGE_SIZE}&from=0",
            callback=self.parse_list,
            cb_kwargs={"offset": 0},
        )

    def parse_list(self, response, offset):
        """Parse JSON response from search API and follow article links."""
        data = response.json()

        # The API returns a list of article objects at the top level or nested
        # under a key — try both shapes.
        if isinstance(data, list):
            articles = data
        else:
            articles = (
                data.get("results")
                or data.get("items")
                or data.get("data")
                or []
            )

        if not articles:
            # No more results — stop pagination
            return

        for article in articles:
            url = article.get("url") or article.get("link") or article.get("href")
            if url:
                yield response.follow(
                    url,
                    callback=self.parse_article,
                    meta={"source_url": response.url},
                )

        # Fetch next page
        next_offset = offset + PAGE_SIZE
        yield scrapy.Request(
            url=f"{SEARCH_API}?size={PAGE_SIZE}&from={next_offset}",
            callback=self.parse_list,
            cb_kwargs={"offset": next_offset},
        )

    def parse_article(self, response):
        """Extract article data from a TechTudo article page."""
        link = response.url

        # Title
        title = response.css("h1.content-head__title::text").get()
        if not title:
            title = response.css("title::text").get()
        if title:
            title = title.strip()

        # Author
        author = response.css(
            "p.content-publication-data__from::attr(title)"
        ).get()
        if not author:
            author = response.css(
                "span.content-publication-data__from::text"
            ).get()
        if not author:
            author = response.css(
                "a.content-publication-data__from::text"
            ).get()
        if not author:
            author = response.xpath(
                "//meta[@name='author']/@content"
            ).get()
        if author:
            author = author.strip()

        # Published date
        published_date = response.xpath(
            "//meta[@property='article:published_time']/@content"
        ).get()
        if not published_date:
            published_date = response.css("time[datetime]::attr(datetime)").get()

        # Body text
        paragraphs = response.css(
            "article p.content-text__container::text"
        ).getall()
        text = " ".join(p.strip() for p in paragraphs if p.strip())
        if not text:
            text = response.xpath(
                "//meta[@property='og:description']/@content"
            ).get()

        # Category extracted from URL path, e.g. /noticias/2024/...
        category_match = re.search(
            r"techtudo\.com\.br/([^/]+)/\d{4}/", link
        )
        category = category_match.group(1) if category_match else None

        # Metadata
        source_url = response.meta.get("source_url")
        collected_at = datetime.now(timezone.utc).isoformat()

        yield TechTudoJogosSpiderItem(
            title=title,
            author=author,
            text=text,
            link=link,
            published_date=published_date,
            category=category,
            collected_at=collected_at,
            source_url=source_url,
        )
