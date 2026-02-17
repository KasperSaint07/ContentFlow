from typing import Type

from sqlalchemy.orm import Session

from app.models import Article, Source
from app.scrapers.base import BaseScraper

from app.scrapers.zakon import ZakonScraper

SCRAPER_REGISTRY: dict[str, Type[BaseScraper]] = {
    "Zakon.kz": ZakonScraper,
}


def _ensure_default_sources(db: Session) -> None:
    """Create built-in sources for fresh databases (idempotent)."""
    defaults = [
        {"name": "Zakon.kz", "base_url": "https://www.zakon.kz"},
    ]

    created = False
    for item in defaults:
        exists = db.query(Source).filter(Source.name == item["name"]).first()
        if exists:
            continue
        db.add(
            Source(
                name=item["name"],
                base_url=item["base_url"],
                is_active=True,
            )
        )
        created = True

    if created:
        db.commit()


def run_for_source(db: Session, source_id: int) -> tuple[int, int]:
    source = db.query(Source).filter(Source.id == source_id, Source.is_active).first()
    if not source:
        return 0, 0

    scraper_class = SCRAPER_REGISTRY.get(source.name)
    if not scraper_class:
        return 0, 0

    scraper = scraper_class()
    try:
        articles_data = scraper.fetch_articles()
    except Exception:
        db.rollback()
        return 0, 0

    created = 0
    updated = 0

    for data in articles_data:
        existing = (
            db.query(Article)
            .filter(Article.source_id == source_id, Article.url == data.url)
            .first()
        )

        if existing:
            existing.title = data.title
            if data.summary is not None:
                existing.summary = data.summary
            if data.content is not None:
                existing.content = data.content
            if data.published_at is not None:
                existing.published_at = data.published_at
            updated += 1
        else:
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
    _ensure_default_sources(db)
    sources = db.query(Source).filter(Source.is_active).all()
    result = {}
    for source in sources:
        c, u = run_for_source(db, source.id)
        result[source.id] = (c, u)
    return result



