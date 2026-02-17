"""Сервис парсинга: запускаем парсер и сохраняем статьи в БД."""
from typing import Type

from sqlalchemy.orm import Session

from app.models import Article, Source
from app.scrapers.base import BaseScraper, ArticleData


# Словарь: имя источника (как в БД) -> класс парсера
from app.scrapers.zakon import ZakonScraper

SCRAPER_REGISTRY: dict[str, Type[BaseScraper]] = {
    "Zakon.kz": ZakonScraper,
}


def run_for_source(db: Session, source_id: int) -> tuple[int, int]:
    """
    Запустить парсер для одного источника и сохранить статьи в БД.
    Возвращает (сколько создано новых, сколько обновлено).
    """
    # Найти источник в БД
    source = db.query(Source).filter(Source.id == source_id, Source.is_active).first()
    if not source:
        return 0, 0

    # Есть ли парсер для такого источника?
    scraper_class = SCRAPER_REGISTRY.get(source.name)
    if not scraper_class:
        return 0, 0

    # Запустить парсер и получить список статей
    scraper = scraper_class()
    try:
        articles_data = scraper.fetch_articles()
    except Exception:
        return 0, 0

    created = 0
    updated = 0

    for data in articles_data:
        # Ищем статью с таким же source_id и url
        existing = (
            db.query(Article)
            .filter(Article.source_id == source_id, Article.url == data.url)
            .first()
        )

        if existing:
            # Обновляем существующую
            existing.title = data.title
            if data.summary is not None:
                existing.summary = data.summary
            if data.content is not None:
                existing.content = data.content
            if data.published_at is not None:
                existing.published_at = data.published_at
            updated += 1
        else:
            # Создаём новую запись
            new_article = Article(
                source_id=source_id,
                title=data.title,
                url=data.url,
                summary=data.summary,
                content=data.content,
                published_at=data.published_at,
            )
            db.add(new_article)
            created += 1

    db.commit()
    return created, updated


def run_all(db: Session) -> dict[int, tuple[int, int]]:
    """
    Запустить парсинг для всех активных источников.
    Возвращает словарь: {source_id: (created, updated)}.
    """
    sources = db.query(Source).filter(Source.is_active).all()
    result = {}
    for source in sources:
        c, u = run_for_source(db, source.id)
        result[source.id] = (c, u)
    return result



