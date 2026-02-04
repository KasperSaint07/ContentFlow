"""Article schemas."""
from datetime import datetime

from pydantic import BaseModel

from app.schemas.source import SourceResponse


class ArticleResponse(BaseModel):
    """Full article for API (single item)."""

    id: int
    source_id: int
    title: str
    url: str
    summary: str | None = None
    content: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    created_at: datetime | None = None
    source: SourceResponse | None = None

    model_config = {"from_attributes": True}


class ArticleList(BaseModel):
    """Short article for list views."""

    id: int
    source_id: int
    title: str
    url: str
    summary: str | None = None
    published_at: datetime | None = None
    source: SourceResponse | None = None

    model_config = {"from_attributes": True}
