# Phase 3 — Develop

**AI-SDLC Phase:** Code generation, implementation across all layers  
**Status:** ✅ Complete  
**Dates:** 2026-04-13 to 2026-05-10  
**AI Tool:** Claude Code — primary code author under developer direction

---

## Objective

Generate all application code from the specifications and architecture
decisions made in Phases 1–2.  Developer role: provide domain content, review
output, correct mismatches, make architectural calls.

---

## Development Sessions

### Session 1 — 2026-04-13: Full Project Scaffold

**Prompt:**
> "Create a complete FastAPI medistock project with clean architecture.
> Create all folders, `__init__.py` files, and the following files with
> exact content: [all domain models, services, dependencies, main.py].
> Also create a requirements.txt. Finally run: pip install -r requirements.txt"

**Claude generated:**

| File | What Claude inferred |
|------|---------------------|
| `medistock/interfaces/api/routers/patients.py` | Pydantic schemas, CRUD endpoints, 404/422/409 handling |
| `medistock/interfaces/api/routers/doctors_rooms.py` | Doctors + Rooms in one router module, split at import time |
| `medistock/interfaces/api/routers/appointments.py` | Status-transition PATCH endpoints, nested response |
| `medistock/interfaces/api/routers/inventory.py` | Medication CRUD + stock add/dispense endpoints |
| All `__init__.py` files | Package markers inferred from directory structure |
| `requirements.txt` | Inferred from imports in supplied code |

**Developer supplied (exact content):**
- All six domain model files
- `domain/services.py` (BookingService, InventoryService, ABCs)
- `interfaces/api/dependencies.py` (in-memory DI)
- `interfaces/api/main.py` (app factory)

---

### Session 2 — 2026-04-18: SQLAlchemy Infrastructure

**Prompt 3:**
> "Create the SQLAlchemy infrastructure layer with: a database session setup
> using PostgreSQL, SQLAlchemy ORM models for all six entities, repository
> implementations for all abstract repositories, and an alembic migration setup."

**Claude generated (full list):**

```
medistock/infrastructure/
├── __init__.py
├── database.py                          ← engine, SessionLocal, get_db()
├── orm/
│   ├── __init__.py
│   └── models.py                        ← all 6 ORM mapped classes
└── repositories/
    ├── __init__.py
    ├── base.py                          ← build_*, *_to_orm, safe_commit
    ├── patient_repository.py
    ├── doctor_repository.py
    ├── room_repository.py
    ├── medication_repository.py
    ├── appointment_repository.py
    └── stock_repository.py

medistock/interfaces/api/
└── db_dependencies.py                   ← all 6 Depends() providers

alembic.ini
alembic/
├── env.py
├── script.py.mako
└── versions/.gitkeep
```

**Prompt 4:**
> "Create a .env with DATABASE_URL. Make sure python-dotenv and psycopg2-binary
> are in requirements.txt. Switch all routers to use the PostgreSQL repositories.
> Run the alembic migrations."

**Claude did:**
- Added `load_dotenv()` to both `database.py` and `alembic/env.py`
- Changed one import line per router: `dependencies` → `db_dependencies`
- Ran `alembic revision --autogenerate -m "initial schema"` → 6-table migration
- Ran `alembic upgrade head` → tables created in PostgreSQL

---

### Session 3 — 2026-04-19: Bug Fix

**Prompt 5 (bug report):**
> "I'm getting a 500 Internal Server Error on POST /api/v1/doctors/
> Please check the VSCode terminal logs and fix the error."

**Claude diagnosed:**

`session.merge()` keys on primary key only.  New Doctor = new UUID →
always INSERT → hits `UNIQUE` on `ix_doctors_email` → `IntegrityError` →
unhandled 500.

**Claude fixed:**
- Added `DuplicateEntryError` exception class
- Added `safe_commit()` context manager with rollback
- Updated all six `save()` methods
- Added `except DuplicateEntryError → HTTP 409` in all create endpoints

---

### Session 4 — 2026-05-10: Web UI

**Prompt:**
> "Create a minimal but clean web UI for MediStock at /ui. Single HTML file
> at medistock/interfaces/web/static/index.html. Serve it via FastAPI.
> Four tabs: Patients, Doctors, Appointments, Inventory."

**Claude generated:**
- `medistock/interfaces/web/static/index.html` — 400+ lines of HTML/CSS/JS
- Vanilla JS with `async/await` fetch, toast notifications, responsive grid
- All form fields matched to actual API schemas (required two iterations
  after reading the router files to get field names right)
- Updated `main.py`: StaticFiles mount, `/` redirect, `/ui` FileResponse
- Added `aiofiles` to `requirements.txt`

---

### Session 5 — 2026-05-10: Application Layer

**Prompt:**
> "Create medistock/application/use_cases.py with BookingUseCase and
> InventoryUseCase. Wire them into the existing routers."

**Claude generated:**
- `medistock/application/__init__.py`
- `medistock/application/use_cases.py` — `BookingUseCase`, `InventoryUseCase`
- Added `get_booking_use_case()`, `get_inventory_use_case()` to `db_dependencies.py`
- Rewrote `routers/appointments.py` — 4 deps → 1 use case dep per endpoint
- Rewrote `routers/inventory.py` — stock ops via use case; medication CRUD unchanged

---

## Code Volume

| Layer | Files | Approx lines |
|-------|-------|-------------|
| Domain models + services | 8 | ~350 (human) |
| Infrastructure ORM + repos | 10 | ~500 (Claude) |
| API routers + DI | 8 | ~450 (Claude) |
| Application use cases | 2 | ~100 (Claude) |
| Web UI | 1 | ~500 (Claude) |
| Tests | 10 | ~800 (Claude) |
| Config + DevOps | 8 | ~250 (Claude) |
| **Total** | **47** | **~2950** |

---

## Human vs AI

| Artifact | Owner |
|----------|-------|
| Domain model classes (fields, rules, methods) | **Human** |
| BookingService + InventoryService logic | **Human** |
| Abstract repository ABCs | **Human** |
| All FastAPI routers and Pydantic schemas | **Claude** |
| SQLAlchemy ORM models and all six repositories | **Claude** |
| `object.__new__()` mapper pattern | **Claude** |
| `safe_commit` / `DuplicateEntryError` | **Claude** |
| Web UI HTML/CSS/JS | **Claude** |
| BookingUseCase + InventoryUseCase | **Claude** |
| Alembic env.py + migration scripts | **Claude** |
| requirements.txt | **Claude** |
