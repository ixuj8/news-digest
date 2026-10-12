import os
import yaml
from app.database import SessionLocal
from app.models import Section, Source

def load_sources_from_yaml(yaml_path="../sources.yaml"):
    # Resolve path relative to backend root if necessary
    if not os.path.exists(yaml_path):
        yaml_path = "sources.yaml" # Fallback if run from root

    if not os.path.exists(yaml_path):
        print(f"Error: Could not find sources.yaml at {yaml_path}")
        return

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    db = SessionLocal()
    try:
        for sec_data in data.get("sections", []):
            section_name = sec_data["name"]

            # Check or create section
            section = db.query(Section).filter_by(name=section_name).first()
            if not section:
                section = Section(name=section_name)
                db.add(section)
                db.commit()
                db.refresh(section)
                print(f"Created section: {section_name}")

            # Check or create sources
            for src_data in sec_data.get("sources", []):
                source_name = src_data["name"]
                feed_url = src_data["feed_url"]
                kind = src_data.get("kind", "rss")

                source = db.query(Source).filter_by(feed_url=feed_url).first()
                if not source:
                    source = Source(
                        section_id=section.id,
                        name=source_name,
                        feed_url=feed_url,
                        kind=kind
                    )
                    db.add(source)
                    print(f"  -> Added source: {source_name}")
                else:
                    # Update fields if configuration changed
                    source.name = source_name
                    source.section_id = section.id
                    source.kind = kind

            db.commit()
        print("Successfully synced all sources from YAML!")
    except Exception as e:
        db.rollback()
        print(f"Error syncing sources: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    load_sources_from_yaml()
