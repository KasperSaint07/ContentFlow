# ContentFlow

ContentFlow is a news aggregation service built on FastAPI.
It collects articles from external sources, stores them in PostgreSQL, and serves both JSON API and a simple web UI.

## Features

- FastAPI backend with OpenAPI docs (`/docs`)
- Background scraping for all sources or a specific source
- Automatic periodic scraping every 5 minutes on app startup
- PostgreSQL persistence with SQLAlchemy + Alembic migrations
- Minimal web interface with article list, details, and manual refresh action
- Extensible scraper architecture with source-to-scraper registry

## Tech Stack

- Python 3.12+
- FastAPI, Uvicorn
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- httpx + BeautifulSoup4
- Jinja2 + static CSS/JS

## Project Structure

```text
.
|-- Dockerfile
|-- src/
|   |-- app/
|   |   |-- api/                # REST endpoints
|   |   |-- models/             # SQLAlchemy models
|   |   |-- schemas/            # Pydantic schemas
|   |   |-- scrapers/           # Source scrapers
|   |   |-- services/           # Business logic
|   |   |-- static/             # CSS/JS assets
|   |   |-- templates/          # Jinja2 templates
|   |   |-- config.py           # Env-based configuration
|   |   |-- database.py         # Engine/session/base
|   |   `-- main.py             # FastAPI app entrypoint
|   |-- alembic/
|   |   `-- versions/           # Migration files
|   |-- alembic.ini
|   |-- requirements.txt
|   `-- start.sh                # Container entry script
`-- README.md
```

## Environment Variables

The app checks the following variables in order and uses the first available:

1. `DATABASE_URL`
2. `DATABASE_PRIVATE_URL`
3. `DATABASE_PUBLIC_URL`

Example value:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/contentflow
```

## Local Run

Run all commands from `src/`.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000` - web UI
- `http://127.0.0.1:8000/docs` - Swagger UI
- `http://127.0.0.1:8000/redoc` - ReDoc

## Docker Run

From repository root:

```bash
docker build -t contentflow .
docker run --rm -p 8000:8000 -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/contentflow contentflow
```

Container startup script:

- retries migrations (`alembic upgrade head`) before launch
- starts Uvicorn server on `0.0.0.0:${PORT:-8000}`

## API Overview

### HTML routes

- `GET /` - latest articles page
- `GET /articles` - paginated articles page
- `GET /article/{article_id}` - single article page

### JSON routes

- `GET /api/articles` - paginated article list
  - query: `skip`, `limit`, `source_id`, `from_date`, `to_date`
- `GET /api/articles/{article_id}` - article details
- `POST /api/scrape` - trigger scraping for all active sources (background task)
- `POST /api/scrape/{source_id}` - trigger scraping for one source (background task)

## How Scraping Works

Current default source: `Zakon.kz`.

- On app startup, a background loop starts automatically
- Every 5 minutes it runs scraping for active sources
- Articles are deduplicated by unique pair: `(source_id, url)`
- Existing rows are updated when the same article URL is seen again

You can also trigger scraping manually:

- UI button on the home page
- `POST /api/scrape`
- `POST /api/scrape/{source_id}`

## Add a New Source

1. Add source metadata to `sources` table (`name`, `base_url`, `is_active`)
2. Implement scraper class in `src/app/scrapers/` (inherits `BaseScraper`)
3. Register it in `SCRAPER_REGISTRY` inside `src/app/services/scraping_service.py`
4. Run scrape endpoint and verify inserted/updated rows

## Database and Migrations

Migration files:

- `src/alembic/versions/001_initial_sources_articles.py`
- `src/alembic/versions/002_seed_default_sources.py`

Useful commands (from `src/`):

```bash
python -m alembic upgrade head
python -m alembic current
python -m alembic history
```

## Troubleshooting

- App starts but pages are empty:
  - trigger `POST /api/scrape` and wait for background job completion
- DB connection error:
  - check `DATABASE_URL` and PostgreSQL availability
- No new data from source:
  - verify source site markup and scraper selectors in `src/app/scrapers/`

## License

No license file is currently defined in this repository.
