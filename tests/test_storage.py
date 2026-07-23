import pytest
from spider.storage.db import init_db, reset_engine
from spider.storage.repository import (
    CrawlJobRepository,
    ExtractedDataRepository,
    RawPageRepository,
    get_stats,
)
from spider.utils import config as config_module


class DummyItem:
    def model_dump(self):
        return {
            "source_url": "https://example.com/article",
            "title": "Example",
            "description": "Example description",
            "tags": ["example"],
            "key_entities": ["entity"],
            "summary": "Summary",
            "sentiment": "neutral",
        }


def test_storage_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    config_module.reload_settings()
    reset_engine()
    init_db()

    raw_repo = RawPageRepository()
    extracted_repo = ExtractedDataRepository()

    raw_page = raw_repo.save_raw_page(
        url="https://example.com/article",
        html="<html><body>Hello</body></html>",
        status_code=200,
        headers={"content-type": "text/html"},
    )
    extracted_repo.save_extracted_item(DummyItem(), raw_page_id=raw_page.id)
    raw_repo.mark_processed(raw_page.id, True)

    stats = get_stats()
    assert stats["raw_pages"] == 1
    assert stats["processed_pages"] == 1
    assert stats["extracted_items"] == 1


def test_crawl_job_repository_create_and_update(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "jobs_test.db"))
    config_module.reload_settings()
    reset_engine()
    init_db()

    job_repo = CrawlJobRepository()
    job = job_repo.create_job(target_url="https://example.com", job_name="test_job")

    assert job.id is not None
    assert job.status == "running"
    assert job.target_url == "https://example.com"

    job_repo.increment_counts(job.id, crawled=3, extracted=2)
    job_repo.update_job(job.id, status="done")

    stats = get_stats()
    assert stats["crawl_jobs"] >= 1


def test_list_unprocessed_pages(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "unprocessed_test.db"))
    config_module.reload_settings()
    reset_engine()
    init_db()

    raw_repo = RawPageRepository()
    for i in range(3):
        raw_repo.save_raw_page(
            url=f"https://example.com/page{i}",
            html=f"<html><body>Page {i}</body></html>",
            status_code=200,
            headers={},
        )

    unprocessed = raw_repo.list_unprocessed(limit=10)
    assert len(unprocessed) == 3
