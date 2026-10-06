"""Run both scrapers and write the consolidated dataset and run summary."""

import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import (
    clean_price, clean_quote_marks, clean_rating, clean_tags, clean_text, normalize_url,
)
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price", "rating",
    "author", "tags", "description", "scraped_at",
]
SOURCES = ("Books to Scrape", "Quotes to Scrape")


def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )


def clean_record(raw, scraped_at):
    """Map source values into the fixed common schema."""
    return {
        "source": clean_text(raw.get("source")),
        "source_url": normalize_url(raw.get("source_url")),
        "name_or_title": clean_quote_marks(raw.get("name_or_title")),
        "category": clean_text(raw.get("category")),
        "price": clean_price(raw.get("price")),
        "rating": clean_rating(raw.get("rating")),
        "author": clean_text(raw.get("author")),
        "tags": clean_tags(raw.get("tags")),
        "description": clean_text(raw.get("description")),
        "scraped_at": raw.get("scraped_at") or scraped_at,
    }


def write_outputs(records, report):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / "final_dataset.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    with (OUTPUT_DIR / "summary_report.json").open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")


def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    started_clock = time.perf_counter()
    started_at = datetime.now(timezone.utc)
    started_iso = started_at.isoformat()
    raw_by_source = {source: [] for source in SOURCES}
    for source, scraper_class in ((SOURCES[0], BooksScraper), (SOURCES[1], QuotesScraper)):
        scraper = scraper_class()
        try:
            raw_by_source[source] = scraper.scrape()
            logger.info("Collected %d raw records from %s", len(raw_by_source[source]), source)
        except Exception:
            logger.exception("Unexpected scraper failure for %s; continuing with the other source", source)
        finally:
            scraper.close()

    scraped_at = started_iso
    cleaned_by_source = {source: [] for source in SOURCES}
    rejected_by_source = {source: 0 for source in SOURCES}
    rejected_reasons = Counter()
    for source, raw_records in raw_by_source.items():
        for index, raw in enumerate(raw_records, start=1):
            try:
                cleaned = clean_record(raw, scraped_at)
                reasons = validate_record(cleaned)
            except Exception as exc:
                reasons = ["processing_error"]
                logger.warning("Rejected %s record %d due to processing error: %s", source, index, exc)
                rejected_by_source[source] += 1
                rejected_reasons.update(reasons)
                continue
            if reasons:
                rejected_by_source[source] += 1
                rejected_reasons.update(reasons)
                logger.warning("Rejected %s record %d: %s", source, index, ", ".join(reasons))
                continue
            cleaned_by_source[source].append(cleaned)

    candidates = [record for source in SOURCES for record in cleaned_by_source[source]]
    unique, duplicates = find_duplicates(candidates)
    end_at = datetime.now(timezone.utc)
    duration = round(time.perf_counter() - started_clock, 3)
    report = {
        "start_time": started_iso,
        "end_time": end_at.isoformat(),
        "duration_seconds": duration,
        "raw_records_collected_per_source": {key: len(raw_by_source[key]) for key in SOURCES},
        "records_after_cleaning_per_source": {key: len(cleaned_by_source[key]) for key in SOURCES},
        "rejected_records_per_source": rejected_by_source,
        "rejected_records_by_reason": dict(sorted(rejected_reasons.items())),
        "rejected_record_count": sum(rejected_by_source.values()),
        "duplicate_count": len(duplicates),
        "final_record_count": len(unique),
    }
    write_outputs(unique, report)
    logger.info("Finished: %d final records, %d rejected, %d duplicates", len(unique), report["rejected_record_count"], len(duplicates))
    return report


if __name__ == "__main__":
    main()
