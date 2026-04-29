from __future__ import annotations

from pathlib import Path
import random
from urllib.parse import urlparse

from loguru import logger


class ProxyManager:
    """Manages a proxy pool, rotation, and simple ban tracking."""

    def __init__(self, proxy_file: str = "config/proxies.txt"):
        self.proxy_file = Path(proxy_file)
        self.proxies = self._load_proxies(self.proxy_file)
        self.banned: set[str] = set()
        logger.info(f"ProxyManager loaded {len(self.proxies)} proxies")

    def _load_proxies(self, path: Path) -> list[dict[str, str | None]]:
        if not path.exists():
            logger.warning(f"Proxy file not found at {path}. Running without proxies.")
            return []

        proxies: list[dict[str, str | None]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            proxies.append(self._normalise_proxy(stripped))
        return proxies

    @staticmethod
    def _normalise_proxy(proxy_url: str) -> dict[str, str | None]:
        parsed = urlparse(proxy_url)
        if parsed.scheme and parsed.hostname and parsed.port:
            server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            return {
                "server": server,
                "username": parsed.username,
                "password": parsed.password,
                "raw": proxy_url,
            }
        return {"server": proxy_url, "username": None, "password": None, "raw": proxy_url}

    def get_proxy(self) -> dict[str, str | None] | None:
        available = [proxy for proxy in self.proxies if str(proxy["server"]) not in self.banned]
        if not available:
            if self.proxies:
                logger.warning("All proxies are currently banned or exhausted; clearing ban list")
                self.banned.clear()
                available = self.proxies
            else:
                return None
        return random.choice(available)

    def ban_proxy(self, proxy_server: str) -> None:
        self.banned.add(proxy_server)
        logger.warning(f"Proxy banned: {proxy_server}")
