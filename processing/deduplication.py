"""Fingerprint records to detect equivalent source records."""

import hashlib
import re
import unicodedata


def _normalize_key(value):
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    value = "".join(char for char in value if not unicodedata.category(char).startswith("P"))
    return " ".join(value.split())


def make_fingerprint(record):
    source = _normalize_key(record.get("source"))
    if record.get("source") == "Books to Scrape":
        parts = (source, _normalize_key(record.get("name_or_title")))
    else:
        quote = _normalize_key(record.get("name_or_title"))[:50]
        parts = (source, _normalize_key(record.get("author")), quote)
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen, unique, duplicates = set(), [], []
    for record in records:
        fingerprint = make_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            seen.add(fingerprint)
            unique.append(record)
    return unique, duplicates
