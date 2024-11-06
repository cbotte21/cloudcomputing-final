import scrapy
import redis 
from scrapy.utils.project import get_project_settings
from src.items import ParsedItem
from src.utils import fixUrl
import time

timestamp = int(time.time())

class CrawlSpider(scrapy.Spider):
    name = "crawl"

    custom_settings = {
        "FEEDS": {
            f"s3://searchengine-data/scraped/%(batch_id)d-{timestamp}.json": {
                "format": "jsonlines"
            }
        },
    }
    
    start_urls = [
        'https://stackoverflow.com/questions',
        'https://github.com/trending',
        'https://dev.to',
        'https://www.reddit.com/r/programming',
        'https://www.reddit.com/r/learnprogramming',
        'https://news.ycombinator.com',
        'https://www.freecodecamp.org/news',
        'https://www.geeksforgeeks.org',
        'https://hackernoon.com',
        'https://realpython.com',
        'https://www.codecademy.com/resources/blog',
        'https://css-tricks.com',
        'https://docs.python.org/3/',
        'https://www.tutorialspoint.com',
        'https://medium.com/tag/programming',
        'https://learn.microsoft.com/en-us/dotnet/',
        'https://www.javatpoint.com',
        'https://rust-lang.org/learn',
        'https://www.coursera.org/courses?query=programming',
        'https://www.w3schools.com',
        'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
        'https://www.toptal.com/developers/blog',
        'https://martinfowler.com',
        'https://www.smashingmagazine.com/category/javascript',
        'https://www.fullstackpython.com',
        'https://developer.android.com/docs',
        'https://kotlinlang.org/docs',
        'https://reactjs.org/docs/getting-started.html'
    ]

    def __init__(self):
        self.cnt = 0
        settings = get_project_settings()
        domain = settings.get('REDIS_DOMAIN', 'localhost') # 10 Minute default TTL
        port = settings.get('REDIS_PORT', 6379) # 10 Minute default TTL
        self.cache = redis.Redis(host=domain, port=port)
    
    def parse(self, response):
        self.cnt += 1
        if response.status != 200:
            self.logger.warning(f"[{self.cnt}] Recieved status {response.status} from {response.url}")
            # TODO: If ratelimited cut down on site calls
            return

        self.logger.warning(f"[{self.cnt}] {response.url}")
        
        parsedItem = ParsedItem()
        parsedItem["url"] = response.url
        parsedItem["content"] = response.text

        yield parsedItem    

        for next_page in response.css('nav a::attr(href)').getall():
            next_page = fixUrl(next_page, parsedItem["url"])
            if next_page is not None:
                yield response.follow(next_page, self.parse)