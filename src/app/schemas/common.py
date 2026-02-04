"""Common schemas: pagination."""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query params for list endpoints."""

    skip: int = Field(default=0, ge=0, description="Records to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Page size")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    items: list[T]
    total: int
    skip: int
    limit: int
