import feedparser
from datetime import datetime
import time
from app.database import SessionLocal
from sqlalchemy import text

class BaseScraper:
    def fetch(self):
        raise NotImplementedError("Subclasses must implement fetch()")

class RSSScraper(BaseScraper):
    def __init__(self, source_id: int, feed_url: str):
        self.source_id = source_id
        self.feed_url = feed_url

    def fetch(self):
        print(f"Fetching feed from {self.feed_url}...")
        feed = feedparser.parse(self.feed_url)
        articles = []

        for entry in feed.entries:
            # Extract basic fields safely
            title = entry.get("title", "No Title")
            url = entry.get("link", "")
            snippet = entry.get("summary", entry.get("description", ""))

            # Parse publication date if available
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime.fromtimestamp(time.mktime(entry.published_parsed))

            if url:
                articles.append({
                    "source_id": self.source_id,
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "published_at": published_at
                })

        return articles

    def save_to_db(self, articles):
        db = SessionLocal()
        new_count = 0
        try:
            for art in articles:
                # Check if article already exists by URL (skips duplicates)
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

if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Dynamically query all sources from the database
        result = db.execute(text("SELECT id, feed_url FROM sources")).fetchall()

        for source_id, feed_url in result:
            print(f"\n--- Running scraper for Source ID: {source_id} ({feed_url}) ---")
            scraper = RSSScraper(source_id=source_id, feed_url=feed_url)
            items = scraper.fetch()
            scraper.save_to_db(items)

    finally:
        db.close()
