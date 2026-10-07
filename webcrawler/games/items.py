import scrapy

class TechTudoJogosSpiderItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    text = scrapy.Field()
    link = scrapy.Field()
    published_date = scrapy.Field()
    category = scrapy.Field()
    collected_at = scrapy.Field()
    source_url = scrapy.Field()
