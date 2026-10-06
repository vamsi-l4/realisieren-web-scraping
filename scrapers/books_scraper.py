"""Scraper for Books to Scrape listing pages."""

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://books.toscrape.com/"
SOURCE = "Books to Scrape"


class BooksScraper(BaseScraper):
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
            LOGGER.info("Processing books page %d: %s", page_number, url)
            for item in soup.select("article.product_pod"):
                link = item.select_one("h3 > a")
                price = item.select_one("p.price_color")
                rating = item.select_one("p.star-rating")
                records.append({
                    "source": SOURCE,
                    "source_url": urljoin(url, link.get("href")) if link and link.get("href") else None,
                    "name_or_title": link.get("title") if link else None,
                    "category": None,
                    "price": price.get_text(" ", strip=True) if price else None,
                    "rating": " ".join(rating.get("class", [])[1:]) if rating else None,
                    "author": None,
                    "tags": None,
                    "description": None,
                    "scraped_at": None,
                })
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else None
        return records
