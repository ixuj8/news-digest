import os
import feedparser
from app.scraper import RSSScraper

def test_rss_scraper_parser():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_rss.xml")
    with open(fixture_path, "r", encoding="utf-8") as f:
        xml_content = f.read()

    # Instantiate scraper (source_id and url are dummy values)
    scraper = RSSScraper(source_id=1, url="http://test.local/rss")

    # Parse string data or files
    raw_data = feedparser.parse(xml_content)

    items = scraper.parse(raw_data)

    assert isinstance(items, list)
    if len(items) > 0:
        assert "title" in items[0]
        assert "url" in items[0]
