from __future__ import annotations

import sys

from loguru import logger

from spider.utils.config import ensure_runtime_paths, settings


_CONFIGURED = False


def configure_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    ensure_runtime_paths(settings)
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL.upper(),
        enqueue=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )
    logger.add(
        settings.log_abspath,
        level=settings.LOG_LEVEL.upper(),
        enqueue=False,
        rotation="10 MB",
        retention=5,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )
    _CONFIGURED = True


configure_logger()
