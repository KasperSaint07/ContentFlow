"""Сервис статей: достаём из БД список и одну статью."""
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Article


def get_list(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    source_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> tuple[list[Article], int]:
    """
    Вернуть список статей с пагинацией и фильтрами.
    Возвращает (список статей, общее количество).
    """
    # Запрос: статьи + подгрузить источник (source)
    query = (
        db.query(Article)
        .options(joinedload(Article.source))
        .order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
    )

    # Фильтры
    if source_id is not None:
        query = query.filter(Article.source_id == source_id)
    if from_date is not None:
        query = query.filter(func.date(Article.published_at) >= from_date)
    if to_date is not None:
        query = query.filter(func.date(Article.published_at) <= to_date)

    # Сколько всего записей (с теми же фильтрами)
    total = query.count()

    # Пагинация: пропустить skip, взять limit штук
    articles = query.offset(skip).limit(limit).all()

    return articles, total


def get_by_id(db: Session, article_id: int) -> Article | None:
    """Вернуть одну статью по id или None, если нет."""
    return (
        db.query(Article)
        .options(joinedload(Article.source))
        .filter(Article.id == article_id)
        .first()
    )

