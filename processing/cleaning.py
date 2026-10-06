"""Pure data-cleaning helpers shared by both source pipelines."""

import re
from urllib.parse import urljoin, urlsplit, urlunsplit

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return None
    cleaned = " ".join(str(value).replace("\xa0", " ").split())
    return cleaned or None


def clean_quote_marks(value):
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return cleaned.strip().strip("\"'“”‘’«»„‟").strip() or None


def clean_price(value):
    if value is None:
        return None
    match = re.search(r"\d+(?:[.,]\d{1,2})?", str(value).replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None


def clean_rating(value):
    if value is None:
        return None
    text = clean_text(value).lower()
    for word, rating in RATING_MAP.items():
        if re.search(r"\b" + word + r"\b", text):
            return rating
    match = re.search(r"\b([1-5])\b", text)
    return int(match.group(1)) if match else None


def clean_tags(value):
    if value is None:
        return None
    values = value if isinstance(value, (list, tuple, set)) else str(value).split(";")
    tags = sorted({tag.lower() for item in values if (tag := clean_text(item))})
    return ";".join(tags) if tags else None


def normalize_url(value, base_url=None):
    if not value:
        return None
    url = urljoin(base_url, str(value).strip()) if base_url else str(value).strip()
    parts = urlsplit(url)
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        return None
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, parts.fragment))
