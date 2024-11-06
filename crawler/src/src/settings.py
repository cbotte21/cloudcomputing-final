# Scrapy settings for src project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "src"

SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "src (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16
LOG_LEVEL = 'WARNING'
# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    "src.middlewares.SrcSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "src.middlewares.SrcDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "src.pipelines.RedisPipeline": 1,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
# Start with a higher delay to avoid overwhelming servers
AUTOTHROTTLE_START_DELAY = 10
# Set a higher maximum delay to accommodate websites with high latencies
AUTOTHROTTLE_MAX_DELAY = 120
# Lower the concurrency to avoid making too many requests in parallel
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5
# Enable throttling stats for debugging and tracking how throttling behaves
AUTOTHROTTLE_DEBUG = True
# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 8
# Introduce a larger download delay to space out requests further
DOWNLOAD_DELAY = 10
# Limit concurrent requests per domain to prevent overloading specific servers
CONCURRENT_REQUESTS_PER_DOMAIN = 3
# Configure a random factor in the delay to make it less predictable
RANDOMIZE_DOWNLOAD_DELAY = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

REDIS_DOMAIN='localhost'
REDIS_PORT=6379
CACHE_TTL=600

import os

FEEDS = {
    's3://{AWS_S3_BUCKET}/crawled.json': {
        'format': 'json',
        'overwrite': True,  # Optional, set to True to overwrite existing files
    },
}

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'searchengine-data'
FEED_EXPORT_BATCH_ITEM_COUNT = 25