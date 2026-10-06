# Multi-source scraping assignment

## Overview

This beginner-sized ETL pipeline reads the public practice listings at Books to Scrape and Quotes to Scrape, cleans and validates their records, removes duplicates, and writes one consolidated CSV plus a run report. The implementation uses Python, Requests, Beautiful Soup, and the standard library.

## Requirements and setup

Use Python 3.10–3.12 and install the pinned dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run all tests with `pytest`, then run the complete pipeline with:

```powershell
python main.py
```

The run needs internet access to both public sites. No credentials or browser automation are needed.

## Site observations and pagination

Books listing cards use `article.product_pod`; title and relative product link are in `h3 > a`, price in `p.price_color`, rating in the `p.star-rating` class, and pagination in `li.next > a`. Quotes use `div.quote`, `span.text`, `small.author`, `a.tag`, and the same next-link selector. Each scraper resolves the next link relative to the current page and follows it until absent. A visited-URL set protects against accidental loops; page numbers are never specified in code.

The listing pages do not contain book category or description. Those fields are left empty rather than adding roughly 1,000 detail-page requests or guessing values. Quote `source_url` is the listing page on which the quote appeared.

## Data model

Every CSV row has this fixed order: `source`, `source_url`, `name_or_title`, `category`, `price`, `rating`, `author`, `tags`, `description`, `scraped_at`. Book titles go in `name_or_title`; quote text goes there for quote rows. Non-applicable fields remain empty. Prices are numeric floats, ratings are integers 1–5, tags are lowercase alphabetized values separated by semicolons, and timestamps are UTC ISO 8601 values shared across each run.

## Processing

Cleaning is kept in `processing/cleaning.py`: whitespace and quote-mark cleanup, currency-to-number conversion, word/numeric rating conversion, tag normalization, and HTTP(S) URL resolution/normalization. Validation in `processing/validation.py` returns named rejection reasons for unknown source, empty title/text, invalid HTTP(S) URL, negative/non-numeric price, or rating outside 1–5. Invalid records are logged and excluded.

Fingerprints use SHA-256 over normalized identity fields. Books use source plus normalized title. Quotes use source plus normalized author and the first 50 characters of normalized quote. Normalization applies Unicode compatibility normalization, case folding, punctuation removal, and whitespace collapse. Duplicates are removed from the final CSV and counted in the report.

## Error handling

Both scrapers share a `requests.Session`, a descriptive User-Agent, a 15-second timeout, three retries for 429/500/502/503/504 (with backoff), and a 0.5-second pause between requests. Failed pages are logged and stop that source; the coordinator still attempts the other source. Missing item fields are represented as `None` and rejected only when required validation fields are missing.

## Outputs

- `output/final_dataset.csv`: UTF-8 CSV with a fixed column order.
- `output/summary_report.json`: start/end UTC time, duration, collected and cleaned counts by source, rejected counts and reasons, duplicate count, and final row count.
- `logs/scraper.log`: timestamped progress, warnings, and request errors.

The summary reconciles as total raw records = cleaned valid records + rejected records, and final records = cleaned valid records − duplicates.

## Assumptions and limitations

- These practice sites remain publicly accessible and keep the observed listing markup.
- One missing page ends that source's pagination because the failed response does not provide its next link; the other source is still processed.
- No detail pages are fetched, so listing-only book category and description remain empty.
- Source URL for quotes means the listing page, not an author profile.
- `scraped_at` records when this pipeline run began, not a separate timestamp for every individual field.
- Python 3.13 is outside the assignment's stated 3.10–3.12 target, though this code uses syntax supported from Python 3.10 onward.

## Testing

`pytest` runs offline unit tests for cleaning, validation reasons, and intentionally duplicated book/quote records. Live scraping is exercised separately by `python main.py`.

## AI usage

See [AI_USAGE.md](AI_USAGE.md) for the tools, representative prompts, review changes, and verification record.
