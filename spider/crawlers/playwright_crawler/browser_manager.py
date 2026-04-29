from __future__ import annotations

import random


class BrowserManager:
    """Creates Playwright browser contexts with stealth-friendly defaults."""

    def __init__(self, *, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None

    async def open_page(self, *, proxy: dict | None = None, user_agent: str | None = None):
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Playwright is not installed") from exc

        self.playwright = await async_playwright().start()
        launch_kwargs = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        }
        if proxy:
            launch_kwargs["proxy"] = {
                "server": proxy["server"],
                "username": proxy.get("username"),
                "password": proxy.get("password"),
            }
        self.browser = await self.playwright.chromium.launch(**launch_kwargs)
        context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": random.randint(1200, 1920), "height": random.randint(800, 1080)},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = await context.new_page()
        try:
            from playwright_stealth import stealth_async
        except ImportError:
            stealth_async = None
        if stealth_async is not None:
            await stealth_async(page)
        return context, page

    async def close(self) -> None:
        if self.browser is not None:
            await self.browser.close()
        if self.playwright is not None:
            await self.playwright.stop()
