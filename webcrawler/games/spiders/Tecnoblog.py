import scrapy
from datetime import datetime
from games.items import BookItem

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}

class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            url = response.urljoin(href)
            yield response.follow(url, self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        item = BookItem()
        item["title"] = response.css("div.product_main h1::text").get("").strip()
        price_str = response.css("p.price_color::text").get("").strip()
        try:
            item["price"] = float(price_str.replace("£", "").replace(",", "").strip())
        except ValueError:
            item["price"] = 0.0
        rating_class = response.css("p.star-rating::attr(class)").get("").split()
        rating_word = rating_class[-1] if rating_class else "One"
        item["rating"] = RATING_MAP.get(rating_word, 1)
        avail_texts = " ".join(response.css("p.availability::text").getall())
        item["availability"] = "In stock" in avail_texts
        breadcrumbs = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = breadcrumbs[-1].strip() if breadcrumbs else "Unknown"
        item["description"] = response.css("div#product_description ~ p::text").get("").strip()
        tds = response.css("table.table tr td::text").getall()
        item["upc"] = tds[0].strip() if tds else ""
        try:
            item["num_reviews"] = int(tds[-1].strip()) if tds else 0
        except (ValueError, IndexError):
            item["num_reviews"] = 0
        img_src = response.css("div.item.active img::attr(src)").get("") or response.css("#product_gallery img::attr(src)").get("")
        item["image_url"] = response.urljoin(img_src) if img_src else ""
        item["url"] = response.url
        item["collected_at"] = datetime.utcnow()
        yield item
