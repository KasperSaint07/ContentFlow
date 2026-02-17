from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.article import ArticleList, ArticleResponse
from app.schemas.common import PaginatedResponse
from app.services.article_service import get_by_id, get_list

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=PaginatedResponse[ArticleList])
def list_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source_id: int | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
):
    items, total = get_list(
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
    article = get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article
