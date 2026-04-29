from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from loguru import logger

from spider.ai.extractor import DataExtractor
from spider.ai.provider import get_ai_client
from spider.ai.schemas import get_schema_model
from spider.antidetect.proxy_manager import ProxyManager
from spider.core.queue_manager import QueueManager
from spider.core.session import CrawlSession
from spider.crawlers.playwright_crawler import DynamicSpider
from spider.crawlers.scrapy_crawler import ScrapyCrawler
from spider.storage.db import init_db
from spider.storage.exporter import export_data
from spider.storage.repository import CrawlJobRepository, ExtractedDataRepository, RawPageRepository
from spider.utils.config import settings
from spider.utils.validators import safe_filename, validate_url


@dataclass(slots=True)
class EngineConfig:
    url: str
    depth: int = 2
    use_playwright: bool = False
    enable_ai: bool = True
    use_proxies: bool = False
    concurrency: int = 4
    delay: float = 2.0
    output: str = "db"
    job_name: str = "crawl_job"
    schema: str = "generic"
    max_pages: int = settings.MAX_PAGES_PER_CRAWL


class CrawlEngine:
    """Coordinates crawling, parsing, extraction, and storage."""

    def __init__(self, config: dict):
        self.config = EngineConfig(
            url=validate_url(config["url"]),
            depth=int(config.get("depth", 2)),
            use_playwright=bool(config.get("use_playwright", config.get("dynamic", False))),
            enable_ai=bool(config.get("enable_ai", True)),
            use_proxies=bool(config.get("use_proxies", config.get("proxies", False))),
            concurrency=int(config.get("concurrency", settings.CONCURRENT_REQUESTS)),
            delay=float(config.get("delay", settings.DOWNLOAD_DELAY)),
            output=config.get("output", "db"),
            job_name=config.get("job_name") or safe_filename(config["url"]),
            schema=config.get("schema", "generic"),
            max_pages=int(config.get("max_pages", settings.MAX_PAGES_PER_CRAWL)),
        )
        self.proxy_manager = ProxyManager(settings.PROXY_LIST_PATH) if self.config.use_proxies else None
        self.raw_repo = RawPageRepository()
        self.extracted_repo = ExtractedDataRepository()
        self.job_repo = CrawlJobRepository()
        self.schema_model = get_schema_model(self.config.schema)
        self.ai_client = get_ai_client() if self.config.enable_ai else None
        self.extractor = DataExtractor(self.ai_client, self.schema_model) if self.ai_client else None
        self.static_crawler = ScrapyCrawler(
            proxy_manager=self.proxy_manager,
            delay=self.config.delay,
            randomise_delay=settings.RANDOMISE_DELAY,
            max_pages=self.config.max_pages,
        )
        self.dynamic_crawler = DynamicSpider(proxy_manager=self.proxy_manager)

    async def run(self) -> dict:
        init_db()
        session = CrawlSession(target_url=self.config.url)
        job = self.job_repo.create_job(
            target_url=self.config.url,
            job_name=self.config.job_name,
            config={
                "url": self.config.url,
                "depth": self.config.depth,
                "use_playwright": self.config.use_playwright,
                "enable_ai": self.config.enable_ai,
                "use_proxies": self.config.use_proxies,
                "concurrency": self.config.concurrency,
                "delay": self.config.delay,
                "output": self.config.output,
                "job_name": self.config.job_name,
                "schema": self.config.schema,
                "max_pages": self.config.max_pages,
            },
        )
        session.job_id = job.id
        logger.info(f"Starting crawl job {job.id} for {self.config.url}")

        try:
            pages = await self._crawl_pages()
            for page in pages:
                raw_page = self.raw_repo.save_raw_page(
                    url=page["url"],
                    html=page["html"],
                    status_code=page.get("status"),
                    headers=page.get("headers", {}),
                    job_id=session.job_id,
                )
                session.pages_crawled += 1
                self.job_repo.increment_counts(session.job_id, crawled=1)

                if self.extractor and page.get("html"):
                    extracted = await self.extractor.extract(page["url"], page["html"])
                    if extracted is not None:
                        self.extracted_repo.save_extracted_item(
                            extracted,
                            raw_page_id=raw_page.id,
                            job_id=session.job_id,
                        )
                        self.raw_repo.mark_processed(raw_page.id, True)
                        session.pages_extracted += 1
                        self.job_repo.increment_counts(session.job_id, extracted=1)

            session.finish()
            self.job_repo.update_job(
                session.job_id,
                status="done",
                completed_at=session.completed_at,
            )
            output_path = None
            if self.config.output != "db":
                output_path = export_data(
                    format=self.config.output,
                    output_path=f"data/exports/{safe_filename(self.config.job_name)}",
                    job_id=session.job_id,
                )
            return {
                "job_id": session.job_id,
                "pages_crawled": session.pages_crawled,
                "pages_extracted": session.pages_extracted,
                "output": output_path,
            }
        except Exception as exc:
            logger.exception("Crawl job failed")
            self.job_repo.update_job(
                session.job_id,
                status="failed",
                completed_at=datetime.now(timezone.utc),
            )
            raise exc

    async def _crawl_pages(self) -> list[dict]:
        if self.config.use_playwright:
            queue = QueueManager()
            pages: list[dict] = []
            queue.add(self.config.url, depth=0)
            while queue and len(pages) < self.config.max_pages:
                url, depth = queue.pop()
                result = await self.dynamic_crawler.scrape(url)
                if not result.get("html"):
                    continue
                pages.append(result)
                if depth >= self.config.depth:
                    continue
                for link in self.dynamic_crawler.extract_links(result["html"], result["url"]):
                    queue.add(link, depth=depth + 1)
            return pages
        return await self.static_crawler.crawl(self.config.url, self.config.depth)


async def reprocess_raw_pages(limit: int = 50) -> dict:
    init_db()
    ai_client = get_ai_client()
    if ai_client is None:
        raise RuntimeError("AI provider is disabled; set AI_PROVIDER in .env to reprocess pages")

    raw_repo = RawPageRepository()
    extracted_repo = ExtractedDataRepository()
    extractor = DataExtractor(ai_client, get_schema_model("generic"))
    processed = 0
    for page in raw_repo.list_unprocessed(limit=limit):
        extracted = await extractor.extract(page.url, page.html)
        if extracted is None:
            continue
        extracted_repo.save_extracted_item(
            extracted,
            raw_page_id=page.id,
            job_id=page.crawl_job_id,
        )
        raw_repo.mark_processed(page.id, True)
        processed += 1
    return {"processed": processed}
