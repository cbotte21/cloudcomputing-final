# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class SrcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ParsedItem(scrapy.Item):
    url = scrapy.Field()
    content = scrapy.Field()
