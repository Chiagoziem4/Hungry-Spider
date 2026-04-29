from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    return int(value)


def _parse_float(value: str | None, default: float) -> float:
    if value is None or value == "":
        return default
    return float(value)


@dataclass(slots=True)
class Settings:
    AI_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    DB_ENGINE: str = "sqlite"
    SQLITE_PATH: str = "data/hungry_spider.db"
    POSTGRES_URL: str = "postgresql://user:password@localhost:5432/hungry_spider"
    CONCURRENT_REQUESTS: int = 4
    DOWNLOAD_DELAY: float = 2.0
    RANDOMISE_DELAY: bool = True
    USE_PLAYWRIGHT: bool = False
    MAX_PAGES_PER_CRAWL: int = 50
    USE_PROXIES: bool = False
    PROXY_LIST_PATH: str = "config/proxies.txt"
    ROTATE_PROXY_ON_BAN: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/spider.log"

    @property
    def sqlite_abspath(self) -> Path:
        return ROOT_DIR / self.SQLITE_PATH

    @property
    def log_abspath(self) -> Path:
        return ROOT_DIR / self.LOG_FILE



def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env", override=False)
    return Settings(
        AI_PROVIDER=os.getenv("AI_PROVIDER", "ollama"),
        OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "mistral"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY", ""),
        ANTHROPIC_MODEL=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
        DB_ENGINE=os.getenv("DB_ENGINE", "sqlite"),
        SQLITE_PATH=os.getenv("SQLITE_PATH", "data/hungry_spider.db"),
        POSTGRES_URL=os.getenv(
            "POSTGRES_URL",
            "postgresql://user:password@localhost:5432/hungry_spider",
        ),
        CONCURRENT_REQUESTS=_parse_int(os.getenv("CONCURRENT_REQUESTS"), 4),
        DOWNLOAD_DELAY=_parse_float(os.getenv("DOWNLOAD_DELAY"), 2.0),
        RANDOMISE_DELAY=_parse_bool(os.getenv("RANDOMISE_DELAY"), True),
        USE_PLAYWRIGHT=_parse_bool(os.getenv("USE_PLAYWRIGHT"), False),
        MAX_PAGES_PER_CRAWL=_parse_int(os.getenv("MAX_PAGES_PER_CRAWL"), 50),
        USE_PROXIES=_parse_bool(os.getenv("USE_PROXIES"), False),
        PROXY_LIST_PATH=os.getenv("PROXY_LIST_PATH", "config/proxies.txt"),
        ROTATE_PROXY_ON_BAN=_parse_bool(os.getenv("ROTATE_PROXY_ON_BAN"), True),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        LOG_FILE=os.getenv("LOG_FILE", "logs/spider.log"),
    )


settings = load_settings()


def reload_settings() -> Settings:
    global settings
    settings = load_settings()
    return settings


def ensure_runtime_paths(active_settings: Settings | None = None) -> None:
    current = active_settings or settings
    (ROOT_DIR / "data").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "data" / "exports").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "logs").mkdir(parents=True, exist_ok=True)
    if current.DB_ENGINE == "sqlite":
        current.sqlite_abspath.parent.mkdir(parents=True, exist_ok=True)
    current.log_abspath.parent.mkdir(parents=True, exist_ok=True)
