import scrapy

class BookItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    availability = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    upc = scrapy.Field()
    num_reviews = scrapy.Field()
    image_url = scrapy.Field()
    url = scrapy.Field()
    collected_at = scrapy.Field()
