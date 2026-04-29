from __future__ import annotations

from bs4 import BeautifulSoup
import re


_WHITESPACE_RE = re.compile(r"\s+")


def extract_text(html: str) -> str:
    """Extract readable text from HTML and collapse excessive whitespace."""
    soup = BeautifulSoup(html or "", "lxml")
    text = soup.get_text(" ", strip=True)
    return _WHITESPACE_RE.sub(" ", text).strip()
