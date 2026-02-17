"""Зависимости для роутеров (Depends)."""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Отдать сессию БД на время запроса, потом закрыть."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
