"""Validation rules for the common output schema."""

from math import isfinite
from urllib.parse import urlsplit

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record):
    reasons = []
    if record.get("source") not in VALID_SOURCES:
        reasons.append("unknown_source")
    if not isinstance(record.get("name_or_title"), str) or not record["name_or_title"].strip():
        reasons.append("missing_name_or_title")
    url = record.get("source_url")
    try:
        parts = urlsplit(url or "")
        if parts.scheme not in ("http", "https") or not parts.netloc or "." not in parts.netloc:
            reasons.append("invalid_source_url")
    except (TypeError, ValueError):
        reasons.append("invalid_source_url")
    price = record.get("price")
    if price is not None and (isinstance(price, bool) or not isinstance(price, (int, float)) or not isfinite(price) or price < 0):
        reasons.append("invalid_price")
    rating = record.get("rating")
    if rating is not None and (isinstance(rating, bool) or not isinstance(rating, int) or rating not in range(1, 6)):
        reasons.append("invalid_rating")
    return reasons
