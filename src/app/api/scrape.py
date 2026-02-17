"""Роутер парсинга: запуск сбора статей."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.database import SessionLocal
from app.models.source import Source
from app.services import scraping_service

router = APIRouter(prefix="/scrape", tags=["scrape"])


def _background_scrape_all():
    """Фоновая задача: парсинг всех источников (своя сессия БД)."""
    db = SessionLocal()
    try:
        scraping_service.run_all(db)
    finally:
        db.close()


def _background_scrape_source(source_id: int):
    """Фоновая задача: парсинг одного источника."""
    db = SessionLocal()
    try:
        scraping_service.run_for_source(db, source_id)
    finally:
        db.close()


@router.post("")
def scrape_all(background_tasks: BackgroundTasks):
    """Запустить парсинг для всех активных источников (в фоне)."""
    background_tasks.add_task(_background_scrape_all)
    return {"status": "accepted", "message": "Парсинг запущен для всех источников"}


@router.post("/{source_id}")
def scrape_source(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Запустить парсинг для одного источника (в фоне)."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")

    background_tasks.add_task(_background_scrape_source, source_id)
    return {"status": "accepted", "message": f"Парсинг запущен для {source.name}"}
