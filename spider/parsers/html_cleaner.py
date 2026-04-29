from __future__ import annotations

from bs4 import BeautifulSoup


NOISE_TAGS = {
    "script",
    "style",
    "noscript",
    "svg",
    "iframe",
    "header",
    "footer",
    "nav",
    "aside",
    "form",
    "button",
    "input",
}


def clean_html(html: str) -> str:
    """Remove common boilerplate and noisy markup before text extraction."""
    soup = BeautifulSoup(html or "", "lxml")

    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()

    for selector in ["[role='navigation']", ".ad", ".ads", ".advert", ".cookie-banner"]:
        for node in soup.select(selector):
            node.decompose()

    main = soup.find("main") or soup.find("article") or soup.body or soup
    return str(main)
