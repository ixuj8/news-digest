from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str

class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    kind: str
    section_id: Optional[int] = None

class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    title: str
    url: str
    snippet: Optional[str] = None
    published_at: Optional[datetime] = None
