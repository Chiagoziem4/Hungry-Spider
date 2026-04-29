from __future__ import annotations

import random

from loguru import logger


_FALLBACK_UAS = {
    "chrome": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ],
    "firefox": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    ],
    "edge": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    ],
}


try:
    from fake_useragent import UserAgent

    _ua = UserAgent(browsers=["chrome", "firefox", "edge"])
except Exception:
    _ua = None



def get_random_ua(browser: str | None = None) -> str:
    """Return a realistic random user agent, with a static fallback pool."""
    browser_key = (browser or "chrome").lower()
    if _ua is not None:
        try:
            if browser_key and hasattr(_ua, browser_key):
                return getattr(_ua, browser_key)
            return _ua.random
        except Exception as exc:
            logger.debug(f"fake-useragent lookup failed: {exc}")
    candidates = _FALLBACK_UAS.get(browser_key) or sum(_FALLBACK_UAS.values(), [])
    return random.choice(candidates)
