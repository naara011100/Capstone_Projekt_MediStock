# Phase 5 — Deploy

**AI-SDLC Phase:** Containerisation, CI/CD, cloud deployment, git hygiene  
**Status:** ✅ Complete  
**Date:** 2026-04-19  
**AI Tool:** Claude Code — generated all DevOps artefacts

---

## Objective

Package the application for reliable, reproducible deployment and wire an
automated pipeline that runs tests on every push and ships Docker images on
every version tag.

---

## Prompt Used

> "Create the following for the medistock project:
> 1. GitHub Actions CI workflow — runs on push and PR, sets up Python,
>    installs dependencies, runs pytest tests/unit/ (no DB needed for CI)
> 2. GitHub Actions Release workflow — triggers on git tags (v*), builds
>    and pushes Docker image to GHCR
> 3. GitHub Actions CD workflow — deploys to Render after successful release
> 4. A Dockerfile for the FastAPI app
> 5. A docker-compose.yml with medistock app service and PostgreSQL service.
>    Use python:3.12-slim as the base image."

---

## Artefacts Generated

### Dockerfile — Two-stage Build

```dockerfile
# Stage 1: install packages
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime only
FROM python:3.12-slim
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
COPY --from=builder /install /usr/local
COPY medistock/ medistock/
COPY alembic/ alembic/
COPY alembic.ini alembic.ini
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER app
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
```

**Design decisions:**
- Two stages: builder has pip + build tools; runtime has none → smaller final image
- Non-root `app` user: container does not run as root
- `entrypoint.sh` runs `alembic upgrade head` then `uvicorn` — migrations applied on every start
- `tests/` excluded via `.dockerignore` — not needed at runtime

### entrypoint.sh

```sh
#!/bin/sh
set -e
echo "→ Running Alembic migrations…"
alembic upgrade head
echo "→ Starting MediStock API…"
exec uvicorn medistock.interfaces.api.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers "${WORKERS:-2}"
```

**Why migrations on start:** Alembic's incremental model is idempotent — if
all migrations are applied the command exits immediately.  This is safe for
Render's single-container model and eliminates a separate migration step.

### docker-compose.yml

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U medistock -d medistock"]
      interval: 5s
      retries: 10
  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
```

**`service_healthy` condition** ensures the app container does not start until
PostgreSQL is ready to accept connections — prevents migration failures on cold
starts.

---

## CI/CD Pipelines

### `.github/workflows/ci.yml` — Continuous Integration

```
Trigger: push, pull_request
Python:  3.12
Steps:   pip install -r requirements.txt
         pytest tests/unit/ -v --tb=short
```

Runs only unit tests — no database required in GitHub Actions runners.

### `.github/workflows/release.yml` — Docker Image Release

```
Trigger: tags matching v*
Steps:   docker buildx build
         push to ghcr.io/naara011100/medistock
         Tags: v1.2.3, v1.2, v1, sha-<git-sha>, latest
         Cache: type=gha,mode=max
```

GitHub Actions layer cache (`cache-from: type=gha`) avoids rebuilding unchanged
layers on every tag push.

### `.github/workflows/cd.yml` — Continuous Deployment

```
Trigger: workflow_run (Release completed successfully)
Steps:   curl ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
```

`workflow_run` trigger (not a direct tag trigger) ensures deployment fires only
after the Docker image is confirmed built and pushed.

---

## Git Hygiene

**Problem discovered:** Commits before `.gitignore` existed had tracked:
- All `__pycache__/` directories (56 files)
- `.env` (containing the database password)

**Fix applied:**
```bash
# Create .gitignore covering Python cache, .env, venv, IDE files
# Then remove tracked files from the index:
git rm --cached -r $(git ls-files | grep __pycache__)
git rm --cached .env
git commit -m "chore: add .gitignore and untrack cache + secrets"
```

**Lesson:** `.gitignore` only prevents *future* staging.  Files already tracked
must be explicitly removed from the index with `git rm --cached`.

---

## Deployment Target

| Platform | Config |
|----------|--------|
| GitHub Container Registry | Docker images pushed on each `v*` tag |
| Render | Deploy hook called after Release workflow succeeds |
| Local Docker Compose | `docker compose up --build` — full stack in one command |

---

## Human vs AI

| Task | Owner |
|------|-------|
| Choose Render as deployment platform | Human |
| Two-stage Dockerfile pattern | Claude |
| Non-root user in Dockerfile | Claude |
| Migration-on-start via entrypoint.sh | Claude |
| `service_healthy` condition in docker-compose | Claude |
| GHA layer cache configuration | Claude |
| `workflow_run` trigger for CD (not direct tag) | Claude |
| Identify and clean up tracked secrets | Claude (identified), Human (approved) |
| Final push to GitHub | Human |
