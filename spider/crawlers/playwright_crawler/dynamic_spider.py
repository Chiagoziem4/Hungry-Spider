from __future__ import annotations

import asyncio
from urllib.parse import urldefrag

from bs4 import BeautifulSoup
from loguru import logger

from spider.antidetect.behaviour import human_delay, simulate_mouse_move, simulate_scroll
from spider.antidetect.proxy_manager import ProxyManager
from spider.antidetect.useragent_rotator import get_random_ua
from spider.crawlers.playwright_crawler.browser_manager import BrowserManager
from spider.utils.validators import normalise_url, same_domain


class DynamicSpider:
    """Playwright-based crawler for JavaScript-rendered pages."""

    def __init__(self, proxy_manager: ProxyManager | None = None, *, headless: bool = True):
        self.proxy_manager = proxy_manager
        self.browser_manager = BrowserManager(headless=headless)

    async def scrape(self, url: str, wait_for: str = "networkidle") -> dict:
        proxy = self.proxy_manager.get_proxy() if self.proxy_manager else None
        ua = get_random_ua()
        context, page = await self.browser_manager.open_page(proxy=proxy, user_agent=ua)
        try:
            await human_delay(1.2, 2.4)
            response = await page.goto(url, wait_until=wait_for, timeout=30000)
            await simulate_mouse_move(page)
            await simulate_scroll(page)
            await human_delay(0.8, 1.6)
            html = await page.content()
            return {
                "url": page.url,
                "html": html,
                "status": response.status if response else 0,
                "headers": {},
            }
        except Exception as exc:
            logger.error(f"Dynamic crawl failed for {url}: {exc}")
            return {"url": url, "html": "", "status": 0, "headers": {}, "error": str(exc)}
        finally:
            await context.close()
            await self.browser_manager.close()

    async def scrape_many(self, urls: list[str], concurrency: int = 2) -> list[dict]:
        semaphore = asyncio.Semaphore(concurrency)

        async def run(url: str) -> dict:
            async with semaphore:
                return await self.scrape(url)

        return await asyncio.gather(*(run(url) for url in urls))

    @staticmethod
    def extract_links(html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html or "", "lxml")
        links: list[str] = []
        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            candidate = urldefrag(normalise_url(href, base_url)).url
            if candidate.startswith("http") and same_domain(base_url, candidate):
                links.append(candidate)
        return links
