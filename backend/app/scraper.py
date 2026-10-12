import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import feedparser
from datetime import datetime
from app.database import SessionLocal
from app.models import Source
from sqlalchemy import text
import socket
import json

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Thread: %(threadName)s] %(message)s"
)
logger = logging.getLogger(__name__)

USER_AGENT = "NewsDigestBot/1.0 (+https://github.com/ixuj8/news-digest)"

class BaseScraper(ABC):
    def __init__(self, source_id: int, url: str):
        self.source_id = source_id
        self.url = url

    def is_allowed_by_robots(self) -> bool:
        """Check target site's robots.txt policy."""
        parsed_url = urlparse(self.url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch(USER_AGENT, self.url)
        except Exception:
            # Default to allowed if robots.txt is unreachable
            return True

    @abstractmethod
    def fetch(self):
        """Fetch raw content from the source."""
        pass

    @abstractmethod
    def parse(self, raw_content):
        """Parse raw content into standardized article dicts."""
        pass

    def send_to_tcp_server(self, articles, host="localhost", port=9999):
            if not articles:
                return

            try:
                with socket.create_connection((host, port), timeout=5) as sock:
                    for art in articles:
                        # Convert datetime object to ISO format string for JSON serialization
                        if art.get("published_at"):
                            art["published_at"] = art["published_at"].isoformat()

                        payload = json.dumps(art) + "\n"
                        sock.sendall(payload.encode("utf-8"))
                logger.info(f"Successfully transmitted {len(articles)} items to TCP ingest server.")
            except Exception as e:
                logger.error(f"Failed to connect or send data to TCP server: {e}")

class RSSScraper(BaseScraper):
    def is_allowed_by_robots(self) -> bool:
        """Bypass for known RSS feeds."""
        return True

    def fetch(self):
        if not self.is_allowed_by_robots():
            logger.warning(f"Blocked by robots.txt: {self.url}")
            return None

        logger.info(f"Fetching RSS feed from {self.url}...")
        # handle User-Agent via agent parameter
        return feedparser.parse(self.url, agent=USER_AGENT)

    def parse(self, feed):
        if not feed or not hasattr(feed, "entries"):
            return []

        articles = []
        for entry in feed.entries:
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime.fromtimestamp(time.mktime(entry.published_parsed))

            articles.append({
                "source_id": self.source_id,
                "title": entry.get("title", "No Title"),
                "url": entry.get("link", ""),
                "snippet": entry.get("summary", entry.get("description", "")),
                "published_at": published_at
            })
        return articles

def run_scraper_task(source_id: int, feed_url: str, kind: str):
    """Worker function executed by ThreadPoolExecutor."""
    if kind == "rss":
        scraper = RSSScraper(source_id=source_id, url=feed_url)
        raw_data = scraper.fetch()
        items = scraper.parse(raw_data)
        if items:
            scraper.send_to_tcp_server(items)
        time.sleep(1) # Polite delay per host
    else:
        logger.warning(f"Scraper kind '{kind}' not supported yet.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        sources = db.query(Source).all()

        if not sources:
            logger.info("No sources found in the database.")
        else:
            logger.info(f"Starting concurrent scrape for {len(sources)} sources...")
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(run_scraper_task, source.id, source.feed_url, source.kind)
                    for source in sources
                ]
                for future in as_completed(futures):
                    future.result()
            logger.info("All scraping tasks completed successfully.")
    finally:
        db.close()
