"""Scraper for Quotes to Scrape listing pages."""

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://quotes.toscrape.com/"
SOURCE = "Quotes to Scrape"


class QuotesScraper(BaseScraper):
    def scrape(self):
        records = []
        url = BASE_URL
        visited = set()
        page_number = 0
        while url and url not in visited:
            visited.add(url)
            page_number += 1
            response = self.fetch(url)
            if response is None:
                break
            soup = BeautifulSoup(response.text, "lxml")
            LOGGER.info("Processing quotes page %d: %s", page_number, url)
            for quote in soup.select("div.quote"):
                text = quote.select_one("span.text")
                author = quote.select_one("small.author")
                records.append({
                    "source": SOURCE,
                    "source_url": url,
                    "name_or_title": text.get_text(" ", strip=True) if text else None,
                    "category": None,
                    "price": None,
                    "rating": None,
                    "author": author.get_text(" ", strip=True) if author else None,
                    "tags": [tag.get_text(" ", strip=True) for tag in quote.select("a.tag")],
                    "description": None,
                    "scraped_at": None,
                })
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else None
        return records
