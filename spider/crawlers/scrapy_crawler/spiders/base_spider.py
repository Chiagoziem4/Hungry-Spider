from __future__ import annotations

from loguru import logger

try:
    import scrapy
except ImportError:
    scrapy = None

from spider.storage.repository import RawPageRepository


if scrapy is None:
    class BaseSpider:  # pragma: no cover - used only when Scrapy is unavailable
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Scrapy is not installed")
else:
    class BaseSpider(scrapy.Spider):
        """Common logic shared by Scrapy-based spiders."""

        name = "base"

        def __init__(self, target_url: str | None = None, depth: int = 2, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_urls = [target_url] if target_url else []
            self.depth = depth
            self.repo = RawPageRepository()
            logger.info(f"Spider initialised for {target_url} | depth={depth}")

        def parse(self, response):
            self.repo.save_raw_page(
                url=response.url,
                html=response.text,
                status_code=response.status,
                headers=dict(response.headers),
            )
            yield {
                "url": response.url,
                "html": response.text,
                "status_code": response.status,
                "headers": dict(response.headers),
                "depth": response.meta.get("depth", 0),
            }
            if response.meta.get("depth", 0) < self.depth:
                for href in response.css("a::attr(href)").getall():
                    yield response.follow(
                        href,
                        callback=self.parse,
                        meta={"depth": response.meta.get("depth", 0) + 1},
                        errback=self.handle_error,
                    )

        def handle_error(self, failure):
            logger.warning(f"Request failed: {failure.request.url} | {failure!r}")
