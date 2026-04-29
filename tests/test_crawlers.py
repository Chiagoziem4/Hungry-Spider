from spider.core.queue_manager import QueueManager
from spider.crawlers.scrapy_crawler.runner import ScrapyCrawler



def test_queue_manager_deduplicates_urls():
    queue = QueueManager()

    assert queue.add("https://example.com", depth=0)
    assert not queue.add("https://example.com", depth=1)
    assert len(queue) == 1



def test_static_crawler_extracts_same_domain_links():
    html = """
    <html>
      <body>
        <a href="/about">About</a>
        <a href="https://example.com/contact#team">Contact</a>
        <a href="https://other.com/skip">External</a>
      </body>
    </html>
    """

    links = ScrapyCrawler.extract_links(html, "https://example.com")

    assert "https://example.com/about" in links
    assert "https://example.com/contact" in links
    assert all(link.startswith("https://example.com") for link in links)
