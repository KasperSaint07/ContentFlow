from datetime import datetime

from pydantic import BaseModel


class SourceResponse(BaseModel):
    id: int
    name: str
    base_url: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
