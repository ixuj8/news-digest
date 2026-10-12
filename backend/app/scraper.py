from abc import ABC, abstractmethod
import feedparser
from datetime import datetime
import time
from app.database import SessionLocal
from app.models import Source
from sqlalchemy import text

class BaseScraper(ABC):
    def __init__(self, source_id: int, url: str):
        self.source_id = source_id
        self.url = url

    @abstractmethod
    def fetch(self):
        """Fetch raw content from the source."""
        pass

    @abstractmethod
    def parse(self, raw_content):
        """Parse raw content into standardized article dicts."""
        pass

class RSSScraper(BaseScraper):
    def fetch(self):
        print(f"Fetching RSS feed from {self.url}...")
        return feedparser.parse(self.url)

    def parse(self, feed):
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

    def save_to_db(self, articles):
        db = SessionLocal()
        new_count = 0
        try:
            for art in articles:
                query = text("SELECT id FROM articles WHERE url = :url")
                existing = db.execute(query, {"url": art["url"]}).fetchone()

                if not existing:
                    insert_query = text("""
                        INSERT INTO articles (source_id, title, url, snippet, published_at)
                        VALUES (:source_id, :title, :url, :snippet, :published_at)
                    """)
                    db.execute(insert_query, art)
                    new_count += 1
            db.commit()
            print(f"Successfully added {new_count} new articles.")
        except Exception as e:
            db.rollback()
            print(f"Error saving articles: {e}")
        finally:
            db.close()

class HTMLScraper(BaseScraper):
    def fetch(self):
        print(f"Fetching HTML page from {self.url}...")
        # Stub: Implement requests + BeautifulSoup logic later
        return None

    def parse(self, html_content):
        # Stub for custom HTML parsing
        return []

if __name__ == "__main__":
    db = SessionLocal()
    try:
        sources = db.query(Source).all()

        if not sources:
            print("No sources found in the database. Run `python -m app.loader` first!")

        for source in sources:
            print(f"\n--- Running scraper for: {source.name} ({source.feed_url}) ---")
            if source.kind == "rss":
                scraper = RSSScraper(source_id=source.id, url=source.feed_url)
                raw_data = scraper.fetch()
                items = scraper.parse(raw_data)
                scraper.save_to_db(items)
            else:
                print(f"Scraper kind '{source.kind}' not supported yet.")
    finally:
        db.close()
