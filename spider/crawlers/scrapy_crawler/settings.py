from spider.utils.config import settings as app_settings

BOT_NAME = "hungry_spider"
SPIDER_MODULES = ["spider.crawlers.scrapy_crawler.spiders"]
NEWSPIDER_MODULE = "spider.crawlers.scrapy_crawler.spiders"

CONCURRENT_REQUESTS = app_settings.CONCURRENT_REQUESTS
DOWNLOAD_DELAY = app_settings.DOWNLOAD_DELAY
RANDOMIZE_DOWNLOAD_DELAY = app_settings.RANDOMISE_DELAY
CONCURRENT_REQUESTS_PER_DOMAIN = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

DOWNLOADER_MIDDLEWARES = {
    "spider.crawlers.scrapy_crawler.middlewares.RandomUserAgentMiddleware": 400,
    "spider.crawlers.scrapy_crawler.middlewares.ProxyRotatorMiddleware": 410,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
}

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]

ITEM_PIPELINES = {
    "spider.crawlers.scrapy_crawler.pipelines.AIProcessingPipeline": 300,
    "spider.crawlers.scrapy_crawler.pipelines.DatabasePipeline": 400,
}

ROBOTSTXT_OBEY = False
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

LOG_LEVEL = "WARNING"
