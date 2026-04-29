from __future__ import annotations

from spider.antidetect.proxy_manager import ProxyManager
from spider.antidetect.useragent_rotator import get_random_ua
from spider.utils.config import settings


class RandomUserAgentMiddleware:
    """Injects a random User-Agent into each Scrapy request."""

    def process_request(self, request, spider):
        request.headers["User-Agent"] = get_random_ua()
        return None


class ProxyRotatorMiddleware:
    """Rotates proxies for Scrapy requests and bans on common block statuses."""

    def __init__(self):
        self.proxy_manager = ProxyManager(settings.PROXY_LIST_PATH)

    def process_request(self, request, spider):
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            request.meta["proxy"] = proxy["server"]
        return None

    def process_response(self, request, response, spider):
        if response.status in (403, 429) and "proxy" in request.meta:
            self.proxy_manager.ban_proxy(request.meta["proxy"])
        return response
