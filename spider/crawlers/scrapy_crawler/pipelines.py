from __future__ import annotations

import asyncio

from spider.storage.repository import ExtractedDataRepository, RawPageRepository


class AIProcessingPipeline:
    """Optional Scrapy pipeline that runs AI extraction when configured on the spider."""

    def process_item(self, item, spider):
        extractor = getattr(spider, "extractor", None)
        if extractor is None:
            return item
        result = asyncio.run(extractor.extract(item["url"], item["html"]))
        if result is not None:
            item["extracted"] = result
        return item


class DatabasePipeline:
    """Persist raw and extracted data from Scrapy item output."""

    def __init__(self):
        self.raw_repo = RawPageRepository()
        self.extracted_repo = ExtractedDataRepository()

    def process_item(self, item, spider):
        raw_page = self.raw_repo.save_raw_page(
            url=item["url"],
            html=item["html"],
            status_code=item.get("status_code"),
            headers=item.get("headers", {}),
            job_id=item.get("job_id"),
        )
        if item.get("extracted") is not None:
            self.extracted_repo.save_extracted_item(
                item["extracted"],
                raw_page_id=raw_page.id,
                job_id=item.get("job_id"),
            )
        return item
