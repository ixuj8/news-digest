CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE sections (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL            -- tech, world, entertainment
);

CREATE TABLE sources (
  id SERIAL PRIMARY KEY,
  section_id INT REFERENCES sections(id),
  name TEXT NOT NULL,
  feed_url TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'rss'     -- rss or html
);

CREATE TABLE articles (
  id SERIAL PRIMARY KEY,
  source_id INT REFERENCES sources(id),
  url TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  snippet TEXT,                        -- short excerpt only, never full text
  published_at TIMESTAMPTZ,
  embedding VECTOR(1536),              -- match embeddings model
  cluster_id INT
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  github_id BIGINT UNIQUE NOT NULL,
  login TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE user_sections (
  user_id INT REFERENCES users(id),
  section_id INT REFERENCES sections(id),
  PRIMARY KEY (user_id, section_id)
);

CREATE TABLE user_topics (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  section_id INT REFERENCES sections(id),
  topic TEXT NOT NULL,                 -- 'Grammys', 'Dune', a singer
  embedding VECTOR(1536)
);

CREATE TABLE clusters (
  id SERIAL PRIMARY KEY,
  section_id INT REFERENCES sections(id),
  day DATE NOT NULL,
  summary TEXT,                        -- one LLM summary shared by all users
  article_count INT NOT NULL           -- cheap proxy for how significant the story is
);

CREATE TABLE digests (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  day DATE NOT NULL,
  content JSONB NOT NULL,              -- ordered cluster ids plus per-topic highlights
  UNIQUE (user_id, day)
);
