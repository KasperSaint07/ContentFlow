"""Роутер статей: список и одна статья."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.article import ArticleList, ArticleResponse
from app.schemas.common import PaginatedResponse
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=PaginatedResponse[ArticleList])
def list_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source_id: Optional[int] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
):
    """Получить список статей с пагинацией и фильтрами."""
    items, total = article_service.get_list(
        db,
        skip=skip,
        limit=limit,
        source_id=source_id,
        from_date=from_date,
        to_date=to_date,
    )
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Получить одну статью по id."""
    article = article_service.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article
