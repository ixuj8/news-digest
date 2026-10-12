ALTER TABLE sections ADD COLUMN slug VARCHAR(255);

UPDATE sections
SET slug = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g'))
WHERE slug IS NULL;

-- Make slugs mandatory
ALTER TABLE sections ALTER COLUMN slug SET NOT NULL;

-- Ensure no two sections can have the same slug
ALTER TABLE sections ADD CONSTRAINT unique_section_slug UNIQUE (slug);
