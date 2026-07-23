from spider.antidetect.header_factory import build_headers
from spider.antidetect.proxy_manager import ProxyManager
from spider.antidetect.useragent_rotator import get_random_ua
from spider.antidetect.behaviour import compute_delay


def test_proxy_manager_loads_and_bans(tmp_path):
    proxy_file = tmp_path / "proxies.txt"
    proxy_file.write_text(
        "# comment\nhttp://user:pass@proxy.example.com:8080\nhttp://proxy2.example.com:8081\n",
        encoding="utf-8",
    )
    manager = ProxyManager(str(proxy_file))
    assert len(manager.proxies) == 2
    proxy = manager.get_proxy()
    assert proxy is not None
    manager.ban_proxy(str(proxy["server"]))
    assert str(proxy["server"]) in manager.banned


def test_header_factory_includes_user_agent():
    headers = build_headers(referer="https://example.com")
    assert headers["User-Agent"]
    assert headers["Referer"] == "https://example.com"


def test_get_random_ua_returns_valid_string():
    ua = get_random_ua()
    assert isinstance(ua, str)
    assert len(ua) > 10


def test_build_headers_without_referer():
    headers = build_headers()
    assert "User-Agent" in headers
    assert "Referer" not in headers


def test_compute_delay_without_randomise():
    delay = compute_delay(2.0, randomise=False)
    assert delay == 2.0


def test_compute_delay_with_randomise_stays_above_base():
    delay = compute_delay(2.0, randomise=True)
    assert delay >= 2.0
