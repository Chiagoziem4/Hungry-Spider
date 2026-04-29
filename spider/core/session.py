from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class CrawlSession:
    target_url: str
    job_id: int | None = None
    pages_crawled: int = 0
    pages_extracted: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)

    def finish(self) -> None:
        self.completed_at = datetime.now(timezone.utc)
