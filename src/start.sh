#!/bin/sh
set -u

MAX_ATTEMPTS="${DB_MIGRATION_MAX_ATTEMPTS:-20}"
SLEEP_SECONDS="${DB_MIGRATION_RETRY_SECONDS:-3}"
ATTEMPT=1

while [ "$ATTEMPT" -le "$MAX_ATTEMPTS" ]; do
  echo "Running migrations (attempt ${ATTEMPT}/${MAX_ATTEMPTS})..."
  if python -m alembic upgrade head; then
    echo "Migrations completed."
    break
  fi

  echo "Migration attempt ${ATTEMPT} failed. Retrying in ${SLEEP_SECONDS}s..."
  ATTEMPT=$((ATTEMPT + 1))
  sleep "$SLEEP_SECONDS"
done

if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
  echo "Migration retries exhausted. Starting app anyway."
fi

exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
