# ── Build stage ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# psycopg2-binary ships its own libpq — no system libs required.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ──────────────────────────────────────────────────────────
FROM python:3.12-slim

# Create a non-root user so the container does not run as root.
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy only the installed packages from the builder layer.
COPY --from=builder /install /usr/local

# Copy application source.
COPY medistock/   medistock/
COPY alembic/     alembic/
COPY alembic.ini  alembic.ini
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Switch to the non-root user for runtime.
USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
