import asyncio
from contextlib import suppress
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.articles import router as articles_router
from app.api.deps import get_db
from app.api.scrape import router as scrape_router
from app.services.article_service import get_by_id, get_list
from app.services.scraping_service import run_all
from app.database import SessionLocal

APP_DIR = Path(__file__).resolve().parent
AUTO_SCRAPE_INTERVAL_SECONDS = 300

app = FastAPI(title="ContentFlow", description="Агрегатор новостей")

app.include_router(articles_router, prefix="/api")
app.include_router(scrape_router, prefix="/api")

app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


def _run_auto_scrape_once():
    db = SessionLocal()
    try:
        run_all(db)
    finally:
        db.close()


async def _auto_scrape_loop():
    while True:
        await asyncio.to_thread(_run_auto_scrape_once)
        await asyncio.sleep(AUTO_SCRAPE_INTERVAL_SECONDS)


@app.on_event("startup")
async def startup_auto_scrape():
    app.state.auto_scrape_task = asyncio.create_task(_auto_scrape_loop())


@app.on_event("shutdown")
async def shutdown_auto_scrape():
    task = getattr(app.state, "auto_scrape_task", None)
    if task is not None:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    articles, total = get_list(db, skip=0, limit=20)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "total": total,
    })


@app.get("/article/{article_id}")
def article_page(request: Request, article_id: int, db: Session = Depends(get_db)):
    article = get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return templates.TemplateResponse("article.html", {
        "request": request,
        "article": article,
    })
