from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.database import SessionLocal
from app.models.source import Source
from app.services.scraping_service import run_all, run_for_source

router = APIRouter(prefix="/scrape", tags=["scrape"])


def _background_scrape_all():
    db = SessionLocal()
    try:
        run_all(db)
    finally:
        db.close()


def _background_scrape_source(source_id: int):
    db = SessionLocal()
    try:
        run_for_source(db, source_id)
    finally:
        db.close()


@router.post("")
def scrape_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(_background_scrape_all)
    return {"status": "accepted", "message": "Парсинг запущен для всех источников"}


@router.post("/{source_id}")
def scrape_source(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")

    background_tasks.add_task(_background_scrape_source, source_id)
    return {"status": "accepted", "message": f"Парсинг запущен для {source.name}"}
