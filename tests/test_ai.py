import asyncio

from spider.ai.extractor import DataExtractor
from spider.ai.schemas import ExtractedItem


class FakeClient:
    async def extract(self, prompt: str, max_tokens: int = 1024) -> str:
        return '```json\n{"title": "Story", "summary": "Useful summary", "tags": ["news"]}\n```'



def test_data_extractor_parses_model_output():
    html = """
    <html><body><main><h1>Story</h1><p>This page contains enough content to exceed the minimum threshold for extraction.</p></main></body></html>
    """
    extractor = DataExtractor(FakeClient(), ExtractedItem)

    result = asyncio.run(extractor.extract("https://example.com/story", html))

    assert result is not None
    assert result.source_url == "https://example.com/story"
    assert result.title == "Story"
    assert result.tags == ["news"]
