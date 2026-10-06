"""Shared HTTP behavior for the practice-site scrapers."""

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOGGER = logging.getLogger(__name__)


class BaseScraper:
    """A polite HTTP client with retries for temporary server failures."""

    def __init__(self, timeout=15, delay=0.5):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ScrapingAssignment/1.0 (educational project; contact: learner@example.com)"
        })
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(("GET",)),
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self._requested = False

    def fetch(self, url):
        """Fetch a page, pausing between requests and logging failures."""
        if self._requested:
            time.sleep(self.delay)
        self._requested = True
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            LOGGER.error("Request failed for %s: %s", url, exc)
            return None

    def close(self):
        self.session.close()
