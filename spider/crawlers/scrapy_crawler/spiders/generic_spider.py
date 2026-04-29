from __future__ import annotations

from spider.crawlers.scrapy_crawler.spiders.base_spider import BaseSpider


class GenericSpider(BaseSpider):
    """General-purpose configurable spider."""

    name = "generic"
