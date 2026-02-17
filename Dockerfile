FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY src/requirements.txt /app/src/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/src/requirements.txt

COPY src /app/src
WORKDIR /app/src

EXPOSE 8000

CMD ["sh", "-c", "python -m alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
