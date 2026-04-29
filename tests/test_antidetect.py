from spider.antidetect.header_factory import build_headers
from spider.antidetect.proxy_manager import ProxyManager



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
