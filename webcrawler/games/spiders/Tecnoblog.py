import scrapy
from games.items import TechTudoJogosSpiderItem

class TechTudoJogosSpider(scrapy.Spider):
    name = "TechTudoJogos"
    allowed_domains = ["techtudo.com.br"]
    start_urls = ["https://www.techtudo.com.br/jogos/"]

    def start_requests(self):
        url = "https://www.techtudo.com.br/jogos/"
        yield scrapy.Request(
            url, 
            callback=self.parse, 
            meta={"playwright": True} 
        )

    def parse(self, response):
        for article in response.css("div.feed-post-body, div.bastian-feed-item"):
            link = article.css("a.feed-post-link::attr(href)").extract_first()
            
            if link:
                yield response.follow(link, self.parse_article)

        next_page = response.css('a.load-more__button::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        link = response.url
        title = response.css("title::text").extract_first()
        author = response.css("p.content-publication-data__from::attr(title)").extract_first()
        if not author:
            author = response.css("span.content-publication-data__from::text").extract_first()
        if not author:
            author = response.css("a.content-publication-data__from::text").extract_first()
            
        text = "".join(response.css("article p.content-text__container::text").extract()).strip()
        notice = TechTudoJogosSpiderItem(title=title, author=author, text=text, link=link)
        yield notice
