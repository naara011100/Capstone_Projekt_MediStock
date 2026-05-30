# MediStock

[![CI](https://github.com/naara011100/Capstone_Projekt_MediStock/actions/workflows/ci.yml/badge.svg)](https://github.com/naara011100/Capstone_Projekt_MediStock/actions/workflows/ci.yml)
[![API Health](https://img.shields.io/website?url=https%3A%2F%2Fmedistock.onrender.com%2Fhealth&label=API&up_message=online&down_message=offline)](https://medistock.onrender.com/health)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/naara011100/Capstone_Projekt_MediStock/pkgs/container/medistock)
[![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)

Hospital management REST API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.
Handles patient registration, doctor scheduling, appointment booking, and medication inventory.

---

## Live

| Endpoint | URL |
|----------|-----|
| Web UI | https://medistock.onrender.com/ui |
| Swagger docs | https://medistock.onrender.com/docs |
| Health check | https://medistock.onrender.com/health |

---

## Health Endpoint

```
GET /health
```

Returns the current service status. No authentication required.

**Response `200 OK`:**

```json
{
  "status": "ok",
  "service": "medistock"
}
```

Use this endpoint to verify the API is reachable before making other requests, or to wire up an uptime monitor.

```bash
curl https://medistock.onrender.com/health
```

---

## Architecture

Four-layer Clean Architecture — domain logic has zero knowledge of FastAPI or SQLAlchemy.

```
Interfaces  →  Application  →  Domain  →  Infrastructure
(FastAPI)      (UseCases)     (Models)    (SQLAlchemy / PostgreSQL)
```

Full diagram and design decisions: [docs/PROJECT.md](docs/PROJECT.md)

---

## API Reference

| Resource | Base path | Operations |
|----------|-----------|-----------|
| Patients | `/api/v1/patients/` | list, create, get, deactivate |
| Doctors | `/api/v1/doctors/` | list, create, get, deactivate |
| Rooms | `/api/v1/rooms/` | list, create, get, toggle availability |
| Appointments | `/api/v1/appointments/` | list, book, get, confirm, complete, cancel, no-show |
| Medications | `/api/v1/inventory/medications` | list, create, get |
| Stock | `/api/v1/inventory/stock` | list, low-stock alerts, add, dispense |

Interactive documentation available at `/docs` (Swagger UI) and `/redoc`.

---

## Quick Start

### Local (with PostgreSQL running)

```bash
# 1. Clone
git clone https://github.com/naara011100/Capstone_Projekt_MediStock.git
cd Capstone_Projekt_MediStock

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure database
cp .env.example .env          # then edit DATABASE_URL

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn medistock.interfaces.api.main:app --reload
# → http://127.0.0.1:8000/ui
```

### Docker Compose (app + PostgreSQL, zero config)

```bash
docker compose up --build
# → http://localhost:8000/ui
```

Migrations run automatically on container start via `entrypoint.sh`.

---

## Tests

```bash
# Unit tests — no database required (also runs in CI)
pytest tests/unit/ -v

# Full suite — requires medistock_test PostgreSQL database
pytest
```

103 tests across unit, integration, and end-to-end layers.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| HTTP framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Container | Docker (python:3.12-slim, non-root) |
| CI | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |
| Hosting | Render |

---

## Repository

**GitHub:** https://github.com/naara011100/Capstone_Projekt_MediStock  
**AI-SDLC workflow:** [AGENTS.md](AGENTS.md)  
**Use case specs:** [docs/specs/](docs/specs/)
