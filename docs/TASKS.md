# MediStock — Project Tasks

**Current lifecycle phase: 🚀 DEPLOYED**

Last updated: 2026-05-10

---

## Completed

### Sprint 1 — Domain + API Scaffold (2026-04-13)
- [x] Define domain models: Patient, Doctor, Room, Appointment, Medication, StockItem
- [x] Implement BookingService with conflict detection
- [x] Implement InventoryService with low-stock alerts
- [x] Scaffold FastAPI app with five routers (patients, doctors, rooms, appointments, inventory)
- [x] In-memory repository implementations for local development

### Sprint 2 — Database Integration (2026-04-18)
- [x] SQLAlchemy ORM models for all six entities
- [x] Concrete repository implementations (`SQLAlchemy*Repository`)
- [x] Alembic migration setup + initial schema migration
- [x] `python-dotenv` integration; `.env` for local DB credentials
- [x] Switch all routers from in-memory to PostgreSQL repositories
- [x] `safe_commit()` context manager + `DuplicateEntryError` → HTTP 409

### Sprint 3 — Quality & Deployment (2026-04-19)
- [x] Fix 500 error on duplicate-email POST /api/v1/doctors/
- [x] 103-test suite: unit (mocked services), integration (TestClient + real DB), e2e (workflow)
- [x] GitHub Actions CI workflow (unit tests on push/PR)
- [x] GitHub Actions Release workflow (Docker image → GHCR on version tag)
- [x] GitHub Actions CD workflow (Render deploy hook after release)
- [x] Two-stage Dockerfile (`python:3.12-slim`, non-root user, `entrypoint.sh`)
- [x] `docker-compose.yml` with postgres:16-alpine + healthcheck
- [x] `.gitignore` for Python + remove tracked secrets from git history

### Sprint 4 — Web UI (2026-05-10)
- [x] Single-page vanilla JS UI at `medistock/interfaces/web/static/index.html`
- [x] Four tabs: Patients, Doctors (+ Rooms), Appointments, Inventory
- [x] FastAPI static file mount + `/ui` route + redirect from `/`
- [x] Forms wired to all existing API endpoints with correct field names
- [x] Toast notifications, status badges, mobile-responsive grid

### Sprint 5 — Application Layer + Docs (2026-05-10)
- [x] `medistock/application/use_cases.py` — `BookingUseCase`, `InventoryUseCase`
- [x] Wire use cases into `appointments` and `inventory` routers
- [x] Add `get_booking_use_case` and `get_inventory_use_case` to `db_dependencies.py`
- [x] `docs/PROJECT.md` — architecture overview and design decisions
- [x] `docs/specs/UC-001-book-appointment.md` — full use case spec
- [x] `docs/specs/UC-002-manage-inventory.md` — full use case spec
- [x] `docs/TASKS.md` — this file

### Sprint 6 — AI-SDLC Documentation (2026-05-10)
- [x] `skills/ai-sdlc-0-bootstrap.md` — environment setup phase
- [x] `skills/ai-sdlc-1-specify.md` — domain specification phase
- [x] `skills/ai-sdlc-2-design.md` — architecture design phase
- [x] `skills/ai-sdlc-3-develop.md` — code generation phase
- [x] `skills/ai-sdlc-4-validate.md` — testing and bug-fix phase
- [x] `skills/ai-sdlc-5-deploy.md` — deployment and CI/CD phase
- [x] `AGENTS.md` restructured as AI-SDLC workflow router
- [x] `scripts/setup-skills.sh` — symlink helper for `.claude/` and `.agents/`

---

## Backlog

### Authentication & Authorization
- [ ] JWT-based authentication (login endpoint, token validation middleware)
- [ ] Role-based access control: Admin, Doctor, Receptionist, Pharmacist
- [ ] Protect write endpoints; allow public read of own appointments

### Patient Portal
- [ ] Patient self-registration and self-service appointment view
- [ ] Email confirmation on appointment booking

### Inventory Enhancements
- [ ] Reorder threshold configurable per medication (currently hardcoded to 10)
- [ ] Expiry date tracking on stock batches
- [ ] Automatic low-stock email/webhook notification

### Operational
- [ ] Pagination on all list endpoints (`?page=&size=`)
- [ ] Structured logging with request-ID correlation
- [ ] Prometheus metrics endpoint (`/metrics`)
- [ ] Database read replica support for heavy list queries

### Developer Experience
- [ ] OpenAPI client generation for frontend consumption
- [ ] Seed script for demo data (`scripts/seed.py`)
- [ ] Local Docker Compose dev profile with hot-reload
