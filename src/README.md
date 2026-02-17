# ContentFlow

Simple FastAPI pet project:
- parse news from web sources
- save articles to PostgreSQL
- show them on a small Jinja2 frontend

## Stack

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- httpx + BeautifulSoup4
- Jinja2 + CSS + JS

## Quick Start

Run all commands inside `src/`.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file (or copy from `.env.example`):

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/contentflow
```

Run migrations:

```bash
python -m alembic upgrade head
```

Start app:

```bash
python -m uvicorn app.main:app --reload
```

Open:
- `http://127.0.0.1:8000`

## API

- `GET /` - html page with article list
- `GET /article/{id}` - html page for one article
- `GET /api/articles` - json list with pagination
- `GET /api/articles/{id}` - json one article
- `POST /api/scrape` - start scrape for all active sources
- `POST /api/scrape/{source_id}` - start scrape for one source

## Add New Source

1. Insert source row into table `sources` (`name`, `base_url`, `is_active`).
2. Create new scraper in `app/scrapers/`.
3. Register scraper in `app/services/scraping_service.py` inside `SCRAPER_REGISTRY`.
