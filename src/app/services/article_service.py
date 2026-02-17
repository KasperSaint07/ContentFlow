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
    query = (
        db.query(Article)
        .options(joinedload(Article.source))
        .order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())
    )

    if source_id is not None:
        query = query.filter(Article.source_id == source_id)
    if from_date is not None:
        query = query.filter(func.date(Article.published_at) >= from_date)
    if to_date is not None:
        query = query.filter(func.date(Article.published_at) <= to_date)

    total = query.count()

    articles = query.offset(skip).limit(limit).all()

    return articles, total


def get_by_id(db: Session, article_id: int) -> Article | None:
    return (
        db.query(Article)
        .options(joinedload(Article.source))
        .filter(Article.id == article_id)
        .first()
    )

