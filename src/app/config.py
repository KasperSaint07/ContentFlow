import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _normalize_postgres_url(url: str) -> str:
    # SQLAlchemy expects "postgresql://", while many platforms provide "postgres://".
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _resolve_database_url() -> str:
    candidates = (
        os.getenv("DATABASE_URL"),
        os.getenv("DATABASE_PRIVATE_URL"),
        os.getenv("DATABASE_PUBLIC_URL"),
    )
    for value in candidates:
        if value:
            return _normalize_postgres_url(value)
    return "postgresql://postgres:postgres@localhost:5432/contentflow"


DATABASE_URL = _resolve_database_url()
