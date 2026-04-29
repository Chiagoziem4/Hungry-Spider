from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select

from spider.storage.db import session_scope
from spider.storage.models import CrawlJob, ExtractedData, RawPage


class RawPageRepository:
    """Persistence helpers for raw page storage."""

    def save_raw_page(
        self,
        *,
        url: str,
        html: str,
        status_code: int | None,
        headers: dict | None,
        job_id: int | None = None,
    ) -> RawPage:
        with session_scope() as session:
            page = RawPage(
                url=url,
                html=html,
                status_code=status_code,
                headers=headers or {},
                crawl_job_id=job_id,
            )
            session.add(page)
            session.flush()
            session.refresh(page)
            return page

    def list_unprocessed(self, limit: int = 50) -> list[RawPage]:
        with session_scope() as session:
            stmt = (
                select(RawPage)
                .where(RawPage.processed.is_(False))
                .order_by(RawPage.crawled_at.asc())
                .limit(limit)
            )
            return list(session.scalars(stmt))

    def mark_processed(self, raw_page_id: int, processed: bool = True) -> None:
        with session_scope() as session:
            page = session.get(RawPage, raw_page_id)
            if page is not None:
                page.processed = processed


class ExtractedDataRepository:
    """Persistence helpers for structured AI output."""

    def save_extracted_item(
        self,
        item: Any,
        *,
        raw_page_id: int | None = None,
        job_id: int | None = None,
    ) -> ExtractedData:
        payload = item.model_dump() if hasattr(item, "model_dump") else dict(item)
        with session_scope() as session:
            record = ExtractedData(
                url=payload.get("source_url") or payload.get("url", ""),
                raw_page_id=raw_page_id,
                crawl_job_id=job_id,
                title=payload.get("title") or payload.get("product_name"),
                description=payload.get("description"),
                author=payload.get("author"),
                published_date=payload.get("published_date"),
                category=payload.get("category"),
                tags=payload.get("tags", []),
                key_entities=payload.get("key_entities", []),
                summary=payload.get("summary"),
                sentiment=payload.get("sentiment"),
                raw_json=payload,
            )
            session.add(record)
            session.flush()
            session.refresh(record)
            return record

    def list_extracted(self, limit: int | None = None, job_id: int | None = None) -> list[ExtractedData]:
        with session_scope() as session:
            stmt = select(ExtractedData).order_by(ExtractedData.extracted_at.desc())
            if job_id is not None:
                stmt = stmt.where(ExtractedData.crawl_job_id == job_id)
            if limit is not None:
                stmt = stmt.limit(limit)
            return list(session.scalars(stmt))


class CrawlJobRepository:
    """Persistence helpers for crawl job lifecycle management."""

    def create_job(self, *, target_url: str, job_name: str, config: dict | None = None) -> CrawlJob:
        with session_scope() as session:
            job = CrawlJob(
                target_url=target_url,
                job_name=job_name,
                status="running",
                started_at=datetime.now(timezone.utc),
                config=config or {},
            )
            session.add(job)
            session.flush()
            session.refresh(job)
            return job

    def update_job(self, job_id: int, **fields: Any) -> None:
        with session_scope() as session:
            job = session.get(CrawlJob, job_id)
            if job is None:
                return
            for key, value in fields.items():
                setattr(job, key, value)

    def increment_counts(self, job_id: int, *, crawled: int = 0, extracted: int = 0) -> None:
        with session_scope() as session:
            job = session.get(CrawlJob, job_id)
            if job is None:
                return
            job.pages_crawled += crawled
            job.pages_extracted += extracted



def get_stats() -> dict[str, int]:
    with session_scope() as session:
        total_raw = session.scalar(select(func.count()).select_from(RawPage)) or 0
        total_processed = (
            session.scalar(select(func.count()).select_from(RawPage).where(RawPage.processed.is_(True)))
            or 0
        )
        total_extracted = session.scalar(select(func.count()).select_from(ExtractedData)) or 0
        total_jobs = session.scalar(select(func.count()).select_from(CrawlJob)) or 0
        return {
            "raw_pages": int(total_raw),
            "processed_pages": int(total_processed),
            "extracted_items": int(total_extracted),
            "crawl_jobs": int(total_jobs),
        }



def serialise_records(records: Iterable[ExtractedData]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for record in records:
        payload.append(
            {
                "id": record.id,
                "url": record.url,
                "title": record.title,
                "description": record.description,
                "author": record.author,
                "published_date": record.published_date,
                "category": record.category,
                "tags": record.tags or [],
                "key_entities": record.key_entities or [],
                "summary": record.summary,
                "sentiment": record.sentiment,
                "raw_json": record.raw_json or {},
                "crawl_job_id": record.crawl_job_id,
                "raw_page_id": record.raw_page_id,
                "extracted_at": record.extracted_at.isoformat() if record.extracted_at else None,
            }
        )
    return payload
