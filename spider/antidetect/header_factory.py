from __future__ import annotations

import random

from spider.antidetect.useragent_rotator import get_random_ua


_ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8",
    "en-US,en;q=0.9,fr;q=0.6",
]



def build_headers(*, referer: str | None = None, browser: str | None = None) -> dict[str, str]:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8",
        "Accept-Language": random.choice(_ACCEPT_LANGUAGES),
        "Cache-Control": "no-cache",
        "DNT": "1",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": get_random_ua(browser),
    }
    if referer:
        headers["Referer"] = referer
    return headers
