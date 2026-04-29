from __future__ import annotations

import asyncio
from collections import deque
from urllib.parse import urldefrag

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from spider.antidetect.behaviour import compute_delay
from spider.antidetect.header_factory import build_headers
from spider.antidetect.proxy_manager import ProxyManager
from spider.utils.validators import normalise_url, same_domain


class ScrapyCrawler:
    """Static crawler adapter with a lightweight async fallback path."""

    def __init__(
        self,
        *,
        proxy_manager: ProxyManager | None = None,
        delay: float = 2.0,
        randomise_delay: bool = True,
        max_pages: int = 50,
        timeout: float = 30.0,
    ):
        self.proxy_manager = proxy_manager
        self.delay = delay
        self.randomise_delay = randomise_delay
        self.max_pages = max_pages
        self.timeout = timeout

    async def crawl(self, start_url: str, depth: int = 2) -> list[dict]:
        logger.info("Starting static crawl")
        return await self._crawl_with_httpx(start_url, depth)

    async def _crawl_with_httpx(self, start_url: str, depth: int) -> list[dict]:
        seen: set[str] = set()
        queue = deque([(start_url, 0)])
        pages: list[dict] = []

        async with httpx.AsyncClient(follow_redirects=True, timeout=self.timeout, verify=False) as client:
            while queue and len(pages) < self.max_pages:
                url, current_depth = queue.popleft()
                url = urldefrag(url).url
                if url in seen:
                    continue
                seen.add(url)

                page = await self.fetch_page(client, url)
                if page is None:
                    continue
                pages.append(page)

                if current_depth >= depth:
                    continue

                for link in self.extract_links(page["html"], url):
                    if link not in seen:
                        queue.append((link, current_depth + 1))
        return pages

    async def fetch_page(self, client: httpx.AsyncClient, url: str) -> dict | None:
        proxy = self.proxy_manager.get_proxy() if self.proxy_manager else None
        headers = build_headers()
        request_kwargs = {"headers": headers}
        if proxy:
            request_kwargs["proxy"] = proxy["raw"]

        await asyncio.sleep(compute_delay(self.delay, self.randomise_delay))
        try:
            try:
                response = await client.get(url, **request_kwargs)
            except TypeError:
                request_kwargs.pop("proxy", None)
                response = await client.get(url, **request_kwargs)

            if response.status_code in (403, 429) and proxy:
                self.proxy_manager.ban_proxy(str(proxy["server"]))
            return {
                "url": str(response.url),
                "html": response.text,
                "status": response.status_code,
                "headers": dict(response.headers),
            }
        except httpx.HTTPError as exc:
            logger.warning(f"Static crawl failed for {url}: {exc}")
            return None

    @staticmethod
    def extract_links(html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html or "", "lxml")
        links: list[str] = []
        for anchor in soup.select("a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            candidate = normalise_url(href, base_url)
            if candidate.startswith("http") and same_domain(base_url, candidate):
                links.append(candidate)
        return links
