from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.routers import auth
from app.database import engine
from app.models import Base

# Import DB session factory and Pydantic models
from app.database import SessionLocal
from app.schemas import SectionResponse, SourceResponse, ArticleResponse
from app.scraper import run_scraper_task

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Digest API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register auth router
app.include_router(auth.router)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Thread: %(threadName)s] %(message)s"
)
logger = logging.getLogger(__name__)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/sections", response_model=List[SectionResponse])
def get_sections(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT id, name, slug FROM sections")).fetchall()
    return [SectionResponse(id=r.id, name=r.name, slug=r.slug) for r in result]

@app.get("/sources", response_model=List[SourceResponse])
def get_sources(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT id, name, url, kind, section_id FROM sources")).fetchall()
    return [SourceResponse(id=r.id, name=r.name, url=r.url, kind=r.kind, section_id=r.section_id) for r in result]

@app.get("/articles", response_model=List[ArticleResponse])
def get_articles(
    section: Optional[str] = Query(None, description="Filter by section slug or ID"),
    q: Optional[str] = Query(None, description="Search keyword in title or snippet"),
    limit: int = Query(50, ge=1, le=200, description="Max number of articles to return"),
    db: Session = Depends(get_db)
):
    query = """
        SELECT a.id, a.source_id, a.title, a.url, a.snippet, a.published_at
        FROM articles a
        JOIN sources s ON a.source_id = s.id
        JOIN sections sec ON s.section_id = sec.id
        WHERE 1=1
    """
    params = {"limit": limit}

    if section:
        # Check if section is numeric ID or slug string
        if section.isdigit():
            query += " AND sec.id = :section_id"
            params["section_id"] = int(section)
        else:
            query += " AND sec.slug = :section_slug"
            params["section_slug"] = section

    if q:
        query += " AND (a.title ILIKE :q OR a.snippet ILIKE :q)"
        params["q"] = f"%{q}%"

    query += " ORDER BY a.published_at DESC NULLS LAST LIMIT :limit"

    result = db.execute(text(query), params).fetchall()

    return [
        ArticleResponse(
            id=r.id,
            source_id=r.source_id,
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            published_at=r.published_at
        ) for r in result
    ]

def run_all_scrapers(db_session_factory):
    """Background job to fetch all sources and run scrapers."""
    db = db_session_factory()
    try:
        sources = db.execute(text("SELECT id, url, kind FROM sources")).fetchall()
        if not sources:
            logger.info("No sources found in database to scrape.")
            return

        logger.info(f"Starting on-demand scrape for {len(sources)} sources...")

        # ThreadPoolExecutor to run scrapers concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            for source in sources:
                executor.submit(run_scraper_task, source.id, source.url, source.kind)

        logger.info("On-demand scrape background job completed.")
    except Exception as e:
        logger.error(f"Error during background scrape: {e}")
    finally:
        db.close()

@app.post("/scrape", status_code=202)
def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger an on-demand scraper run in the background."""
    background_tasks.add_task(run_all_scrapers, SessionLocal)

    return {
        "status": "success",
        "message": "Scrape job triggered successfully and is running in the background."
    }
