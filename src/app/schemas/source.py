"""Source schemas."""
from datetime import datetime

from pydantic import BaseModel


class SourceResponse(BaseModel):
    """Source in API responses."""

    id: int
    name: str
    base_url: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
