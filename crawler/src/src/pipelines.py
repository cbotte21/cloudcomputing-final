# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from src.items import ParsedItem
import boto3
import urllib.parse
from scrapy.exceptions import DropItem
import json


class RedisPipeline:
    def __init__(self, ttl) -> None:
        self.ttl = ttl

    @classmethod
    def from_crawler(cls, crawler):
        ttl = crawler.settings.get('CACHE_TTL', 600) # 10 Minute default TTL
        return cls(ttl)

    def process_item(self, item, spider):
        spider.cache.set(item['url'], '', ex=self.ttl)
        return item

    def search(self, search):
        return self.cache.match(search)
