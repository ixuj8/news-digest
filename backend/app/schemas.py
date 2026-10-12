from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SectionResponse(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

class SourceResponse(BaseModel):
    id: int
    name: str
    url: str
    kind: str
    section_id: Optional[int] = None

    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    id: int
    source_id: int
    title: str
    url: str
    snippet: Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
