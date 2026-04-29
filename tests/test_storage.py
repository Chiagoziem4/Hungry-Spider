from spider.storage.db import init_db, reset_engine
from spider.storage.repository import ExtractedDataRepository, RawPageRepository, get_stats
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
