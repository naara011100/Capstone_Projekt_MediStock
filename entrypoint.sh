#!/bin/sh
set -e

echo "→ Running Alembic migrations…"
alembic upgrade head

echo "→ Starting MediStock API…"
exec uvicorn medistock.interfaces.api.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers "${WORKERS:-2}"
