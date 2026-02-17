"""Точка входа: сборка приложения FastAPI."""
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.articles import router as articles_router
from app.api.scrape import router as scrape_router
from app.api.deps import get_db
from app.services import article_service

# Пути
APP_DIR = Path(__file__).resolve().parent

# Приложение
app = FastAPI(title="ContentFlow", description="Агрегатор новостей")

# Роутеры API
app.include_router(articles_router, prefix="/api")
app.include_router(scrape_router, prefix="/api")

# Статика и шаблоны
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


# --- HTML-страницы ---

@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    """Главная страница: список статей."""
    articles, total = article_service.get_list(db, skip=0, limit=20)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "total": total,
    })


@app.get("/article/{article_id}")
def article_page(request: Request, article_id: int, db: Session = Depends(get_db)):
    """Страница одной статьи."""
    article = article_service.get_by_id(db, article_id)
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return templates.TemplateResponse("article.html", {
        "request": request,
        "article": article,
    })
