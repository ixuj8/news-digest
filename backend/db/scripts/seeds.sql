-- Insert sections first
INSERT INTO sections (name) VALUES ('tech'), ('world'), ('entertainment')
ON CONFLICT (name) DO NOTHING;

-- Insert RSS sources referencing those sections
INSERT INTO sources (section_id, name, url, kind)
VALUES
  (1, 'Hacker News', 'https://news.ycombinator.com/rss', 'rss'),
  (2, 'BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml', 'rss'),
  (3, 'Variety', 'https://variety.com/feed/', 'rss');
