from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin, urlparse
import re


_URL_SCHEME_RE = re.compile(r"^https?$")


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc or not _URL_SCHEME_RE.match(parsed.scheme):
        raise ValueError(f"Invalid target URL: {url}")
    return url



def normalise_url(url: str, base_url: str | None = None) -> str:
    candidate = urljoin(base_url, url) if base_url else url
    parsed = urlparse(candidate)
    fragmentless = parsed._replace(fragment="")
    return fragmentless.geturl()



def same_domain(base_url: str, candidate_url: str) -> bool:
    return urlparse(base_url).netloc == urlparse(candidate_url).netloc



def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "output"



def ensure_parent_dir(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output
