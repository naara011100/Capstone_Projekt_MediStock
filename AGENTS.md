# AI-Assisted Development Log — MediStock

This document records how AI tooling was used across the full development of this project:
what was generated, what was decided manually, architecture choices, bugs encountered,
and lessons learned.

---

## Tool Used

**Claude Code** (Anthropic) — CLI/IDE assistant powered by `claude-sonnet-4-6`
Accessed via the VS Code extension, operating directly on the local repository.

---

## Session Timeline

| Date | Work done |
|---|---|
| 2026-04-13 | Session 1 — Domain models, services, FastAPI layer, AGENTS.md |
| 2026-04-18 | Session 2 — SQLAlchemy infrastructure, Alembic, PostgreSQL wiring |
| 2026-04-19 | Session 3 — Bug fix (500 error), full test suite, CI/CD, Docker, Git push |

---

## Session 1 — 2026-04-13

### Starting state
Empty repository (single `README.md`).

### Prompt 1 — Full project scaffold
> "Create a complete FastAPI medistock project with clean architecture. Create all folders,
> `__init__.py` files, and the following files with exact content: [domain models, services,
> dependencies, main.py]. After creating all files, also create a `requirements.txt` with
> fastapi / uvicorn / pydantic[email] / pytest / httpx. Finally run: pip install -r requirements.txt"

**What was human-authored (supplied as exact file content in the prompt):**
- All six domain model files with field definitions, validation logic, and business rules
- `BookingService` and `InventoryService` with conflict detection and stock management
- `dependencies.py` in-memory DI wiring
- `main.py` app factory

**What Claude inferred and authored:**
- Full directory tree and all `__init__.py` files
- All four FastAPI routers with inline Pydantic schemas and HTTP error handling
- Smoke test confirming 32 routes registered

### Prompt 2 — Documentation
> "Create an AGENTS.md file that documents our AI-assisted development process so far."

Claude authored this file from the conversation context.

---

## Session 2 — 2026-04-18

### Prompt 3 — SQLAlchemy infrastructure layer
> "Create the SQLAlchemy infrastructure layer with:
> - A database session setup using PostgreSQL
> - SQLAlchemy ORM models for Patient, Doctor, Room, Appointment, Medication, StockItem
> - Repository implementations for all abstract repositories defined in domain/services.py
> - An alembic migration setup"

**What Claude generated:**

| File | Purpose |
|---|---|
| `medistock/infrastructure/database.py` | Engine, `SessionLocal`, `get_db()` FastAPI dependency |
| `medistock/infrastructure/orm/models.py` | All 6 ORM mapped classes in one module |
| `medistock/infrastructure/repositories/base.py` | `build_*` (ORM→domain) and `*_to_orm` (domain→ORM) mappers |
| `medistock/infrastructure/repositories/patient_repository.py` | `SQLAlchemyPatientRepository` |
| `medistock/infrastructure/repositories/doctor_repository.py` | `SQLAlchemyDoctorRepository` |
| `medistock/infrastructure/repositories/room_repository.py` | `SQLAlchemyRoomRepository` |
| `medistock/infrastructure/repositories/medication_repository.py` | `SQLAlchemyMedicationRepository` |
| `medistock/infrastructure/repositories/appointment_repository.py` | Implements `AbstractAppointmentRepository` |
| `medistock/infrastructure/repositories/stock_repository.py` | Implements `AbstractStockRepository` |
| `medistock/interfaces/api/db_dependencies.py` | Drop-in replacement for `dependencies.py` using real DB |
| `alembic.ini` | Alembic config with filename template and logging |
| `alembic/env.py` | Imports `Base.metadata`; respects `DATABASE_URL` env var |
| `alembic/script.py.mako` | Migration file template |

**Architecture decisions made in this session:**

- All ORM models in a single file (`orm/models.py`) to avoid SQLAlchemy relationship
  string-resolution issues across packages.
- `object.__new__()` used in all `build_*` mapper functions to bypass `__post_init__`
  validation when hydrating domain objects from the database. This is intentional — data
  from the DB was already validated on write; re-running guards like "scheduled_at must
  be in the future" would reject valid historical records.
- `session.merge()` for all `save()` calls — handles INSERT and UPDATE by primary key
  without needing separate code paths.
- `lazy="joined"` on relationships that are always needed (Appointment → patient/doctor/room,
  StockItem → medication) to avoid N+1 queries.
- `list_low_stock()` implemented as a SQL-level predicate (`quantity <= low_stock_threshold`)
  so it scales with table size rather than fetching all rows into Python.

### Prompt 4 — PostgreSQL wiring and migration
> "Create a .env file with DATABASE_URL=postgresql://postgres:PASSWORT@localhost:5432/medistock.
> Replace 1234 with the actual password. Also make sure python-dotenv and psycopg2-binary are
> in requirements.txt and installed. Then switch all routers to use the PostgreSQL repositories
> and run the alembic migrations."

**What Claude did:**
- Created `.env` with real credentials
- Added `python-dotenv` to `requirements.txt`; installed it
- Added `load_dotenv()` to both `database.py` and `alembic/env.py` so both the app and
  the CLI pick up `.env` without a manual shell export
- Changed the import in all four routers from `dependencies` → `db_dependencies` (single-line
  change per file)
- Ran `alembic revision --autogenerate -m "initial schema"` → generated migration file
- Ran `alembic upgrade head` → created all 6 tables in PostgreSQL

**Tables created:** `patients`, `doctors`, `rooms`, `medications`, `stock_items`, `appointments`
plus the Alembic-managed `alembic_version` table.

---

## Session 3 — 2026-04-19

### Prompt 5 — Bug fix: 500 Internal Server Error on POST /api/v1/doctors/
> "I'm getting a 500 Internal Server Error when calling POST /api/v1/doctors/
> Please check the VSCode terminal logs and fix the error in the doctors router
> or SQLAlchemy repository."

**Root cause diagnosed by Claude:**

`session.merge()` resolves INSERT vs UPDATE using only the primary key (UUID). Every new
`Doctor` object gets a fresh `uuid4`, so `merge()` always attempted an INSERT — even when
an email already existed in the DB. PostgreSQL raised `UniqueViolation` on `ix_doctors_email`.
Nothing caught it → unhandled 500.

The bug was found by starting a local uvicorn server and sending two identical POST requests,
which reproduced it immediately.

**Fix applied:**

1. Added `DuplicateEntryError` exception class and `safe_commit()` context manager to
   `repositories/base.py`. `safe_commit` wraps `db.commit()` and catches `IntegrityError`,
   calls `db.rollback()` (to leave the session in a clean state), then raises `DuplicateEntryError`.

2. Updated all six `save()` methods to use `with safe_commit(self._db): self._db.merge(...)`.

3. Added a separate `except DuplicateEntryError` block in every router create-endpoint,
   returning **409 Conflict** (distinct from **422 Unprocessable** for domain validation errors).

**Decision:** Keep domain validation errors (422) and DB constraint errors (409) as separate
HTTP status codes. They represent different failure modes: the first means the request was
semantically invalid; the second means it conflicted with existing data.

### Prompt 6 — Complete test suite
> "Create a complete test suite for the medistock project:
> 1. Unit tests in tests/unit/ — test BookingService and InventoryService with mocked repositories
> 2. Integration tests in tests/integration/ — test the FastAPI routes using TestClient and a test PostgreSQL database
> 3. E2E tests in tests/e2e/ — test full workflows
> Also create a pytest.ini config file and make sure all tests pass."

**What Claude generated:**

| File | Tests | Strategy |
|---|---|---|
| `tests/conftest.py` | shared fixtures | Session-scoped engine auto-creates `medistock_test` DB; `client` fixture overrides `get_db` and truncates tables after each test |
| `tests/unit/test_booking_service.py` | 20 tests | `MagicMock` repo, no DB |
| `tests/unit/test_inventory_service.py` | 19 tests | `MagicMock` repo, no DB |
| `tests/integration/conftest.py` | fixtures | Pre-created entity fixtures for appointment/inventory tests |
| `tests/integration/test_patients.py` | 10 tests | HTTP layer + real DB |
| `tests/integration/test_doctors.py` | 12 tests | Includes room tests (same router module) |
| `tests/integration/test_appointments.py` | 15 tests | Full status-transition coverage |
| `tests/integration/test_inventory.py` | 15 tests | Medication CRUD + stock lifecycle |
| `tests/e2e/test_workflows.py` | 7 tests | Full HTTP journeys |
| `pytest.ini` | — | `testpaths = tests`, marker definitions |

**Final result: 103 tests, 0 failures.**

**Key fixture design decision:** The `client` fixture (not `autouse`) handles cleanup by
truncating all tables in FK-safe order after each test. Unit tests never request `client`
or `test_engine`, so they run without any DB connection.

**Note on test isolation:** `session.merge()` + `db.commit()` inside each `save()` call
means the test DB session actually commits data. Tests are isolated by truncation after each
function, not by transaction rollback — rollback-based isolation would conflict with the
`commit()` calls in `safe_commit()`.

### Prompt 7 — CI/CD, Docker, docker-compose
> "Create the following for the medistock project:
> 1. GitHub Actions CI workflow — runs on push and PR, unit tests only
> 2. GitHub Actions Release workflow — triggers on git tags (v*), builds and pushes Docker image
> 3. GitHub Actions CD workflow — deploys to Render after successful release
> 4. A Dockerfile for the FastAPI app
> 5. A docker-compose.yml with medistock app service and PostgreSQL service"

**What Claude generated:**

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Push/PR → `pytest tests/unit/` on `ubuntu-latest` with Python 3.12 |
| `.github/workflows/release.yml` | Tag `v*` → multi-tag Docker image pushed to GHCR |
| `.github/workflows/cd.yml` | Release success → `curl` Render deploy hook |
| `Dockerfile` | Two-stage `python:3.12-slim` build; non-root `app` user; `entrypoint.sh` |
| `entrypoint.sh` | Runs `alembic upgrade head` then `uvicorn`; respects `PORT`/`WORKERS` env vars |
| `docker-compose.yml` | `app` + `postgres:16-alpine` with healthcheck; migrations on startup |
| `.dockerignore` | Excludes `.env`, `tests/`, `__pycache__`, IDE files |

**Architecture decisions:**

- Two-stage Docker build: builder installs packages into `/install`; runtime copies only
  that prefix. No build tools in the final image.
- Migrations run in `entrypoint.sh` on every container start — idempotent, zero-downtime
  safe for Alembic's incremental model.
- Release workflow uses `cache-from: type=gha` / `cache-to: type=gha,mode=max` for
  layer caching across runs.
- CD uses `workflow_run` trigger (not direct tag trigger) so deployment only fires after
  the Docker image is confirmed pushed.

### Prompt 8 — Git hygiene and push
> "Initialize a git repository, create a .gitignore for Python and add all files.
> Show me the commands to push to GitHub."

Claude discovered the repo was already initialised with 5 commits, and that earlier commits
had accidentally tracked `__pycache__` directories and the `.env` file (containing the DB
password). Fixed in one commit:

- Created `.gitignore` covering Python cache, virtualenvs, IDEs, `.env*`
- `git rm --cached -r` removed all `__pycache__` entries from the index (56 files)
- `git rm --cached .env` removed the credentials file from tracking
- Committed the cleanup alongside the Docker/CI files

### Prompt 9 — Final push
> "Add all files to git, commit with message 'feat: initial medistock project setup'
> and push to the existing remote repository (Capstone_Projekt_MediStock).
> Make sure .env is in .gitignore before pushing!"

Working tree was already clean. Claude verified `.env` was in `.gitignore` and not tracked,
then ran `git push origin main`.

**Repository live at:** https://github.com/naara011100/Capstone_Projekt_MediStock

---

## Full Prompt List

| # | Prompt summary | Output |
|---|---|---|
| 1 | Full project scaffold with exact domain model content | Project structure, routers, in-memory DI, requirements.txt |
| 2 | Create AGENTS.md | This file (initial version) |
| 3 | SQLAlchemy infrastructure layer + Alembic setup | ORM models, 6 repos, db_dependencies.py, alembic files |
| 4 | .env + dotenv + switch routers to PostgreSQL + run migrations | .env, load_dotenv wiring, router imports changed, DB tables created |
| 5 | Fix 500 on POST /api/v1/doctors/ | `safe_commit` context manager, `DuplicateEntryError`, 409 responses |
| 6 | Complete test suite (unit + integration + e2e) | 103 tests across 9 files, pytest.ini, conftest fixtures |
| 7 | CI/CD + Dockerfile + docker-compose | 3 workflow files, Dockerfile, entrypoint.sh, docker-compose.yml, .dockerignore |
| 8 | Git setup + .gitignore + push commands | .gitignore, cleaned 56 tracked cache files, .env removed from index |
| 9 | Commit and push to GitHub | Verified clean tree and pushed |
| 10 | Update AGENTS.md with full session log | This file (final version) |

---

## Human vs AI Breakdown

### Human-authored (written by hand or supplied as exact content)

| Artifact | Why manual |
|---|---|
| Domain model class definitions (fields, types, validation rules) | Core business logic — deliberate design choice, not inferred |
| `BookingService` and `InventoryService` implementations | Domain use-cases with specific conflict-detection requirements |
| `dependencies.py` in-memory DI wiring | Provided in initial prompt |
| `main.py` app factory | Provided in initial prompt |
| Architecture decision: clean architecture layers | Structural choice made before any code was written |
| Database password and connection string | Credentials |
| Decision to use Render for deployment | Infrastructure choice |

### AI-generated (Claude Code authored from context)

| Artifact | How Claude derived it |
|---|---|
| All FastAPI routers + Pydantic schemas | Inferred from domain models and service interfaces |
| Full SQLAlchemy ORM layer | Derived from domain model structure |
| `object.__new__()` mapper pattern | Identified need to bypass `__post_init__` for DB hydration |
| `safe_commit` / `DuplicateEntryError` pattern | Diagnosed from live uvicorn traceback |
| 103 tests across unit / integration / e2e | Designed from API surface and domain rules |
| Two-stage Dockerfile | Standard best practice applied to project layout |
| CI/CD workflow YAML | Derived from project toolchain (pytest, Docker, Render) |
| `.gitignore` | Standard Python template applied |
| Cleanup of accidentally tracked files | Identified by inspecting `git ls-files` |

---

## Architecture Decisions

### Clean Architecture

```
medistock/
├── domain/              ← pure Python, zero framework imports
│   ├── models/          ← dataclasses + business rules
│   └── services.py      ← use-cases + abstract repository contracts (ABCs)
├── infrastructure/      ← SQLAlchemy ORM + concrete repository implementations
│   ├── orm/models.py
│   └── repositories/
└── interfaces/
    └── api/             ← FastAPI adapts HTTP ↔ domain; two DI sets:
        ├── dependencies.py     ← in-memory (no DB)
        └── db_dependencies.py  ← PostgreSQL (production)
```

The domain layer has **zero** knowledge of FastAPI, SQLAlchemy, or Pydantic. This means:
- Domain logic can be unit-tested with plain `MagicMock` objects
- The persistence backend is swappable without touching domain code
- The HTTP layer is swappable without touching domain or infrastructure code

### Repository Pattern with ABCs

`AbstractAppointmentRepository` and `AbstractStockRepository` in `domain/services.py` define
the persistence contract as Python ABCs. The SQLAlchemy implementations in `infrastructure/`
satisfy these contracts. The in-memory implementations in `interfaces/api/dependencies.py`
also satisfy them — both can be used interchangeably.

### Two DI Modules

`dependencies.py` (in-memory) is kept alongside `db_dependencies.py` (PostgreSQL). This makes
it trivial to run the API locally without a database for rapid prototyping, and to switch to
the real backend by changing a single import line per router.

### Test Isolation Strategy

Integration and E2E tests commit to a real `medistock_test` database (because `safe_commit`
calls `db.commit()` inside each `save()`). Transaction-rollback isolation is incompatible with
this. Instead: a `client` fixture truncates all tables in FK-safe reverse order after each test.
Unit tests use `MagicMock` and never touch any database.

### Docker Migration-on-Start

`entrypoint.sh` runs `alembic upgrade head` before `uvicorn`. This means migrations are applied
automatically on every container start — useful in Render's single-container model. Alembic's
incremental migration model makes this idempotent: if all migrations are already applied, the
command exits immediately.

---

## Lessons Learned

### 1. `session.merge()` is not a unique-constraint-aware upsert

`merge()` keys on the primary key only. Inserting a new domain object (new UUID) with a
duplicate email still hits the DB as an INSERT and raises `IntegrityError`. Always wrap
`save()` in a try/except for `IntegrityError` and return a meaningful HTTP error (409).

### 2. `__post_init__` validation is a write-time guard, not a read-time invariant

Domain dataclasses run `__post_init__` on construction, which includes guards like
"scheduled_at must be in the future". Loading an Appointment from the DB would fail this check.
Solution: use `object.__new__()` in all ORM-to-domain mapper functions to bypass `__post_init__`.

### 3. Commit sensitive files before adding a .gitignore

Previous commits tracked `__pycache__` and `.env` because no `.gitignore` existed at the time
they were added. A `.gitignore` only prevents *future* staging — it does not retroactively
untrack already-committed files. Use `git rm --cached` to remove them from the index.

### 4. Separation of error types matters for API consumers

Using 422 for domain validation failures and 409 for DB constraint conflicts gives API consumers
actionable information. A 422 means "fix your request data"; a 409 means "this resource already
exists". Collapsing both into 500 (the original bug) gives consumers nothing to work with.

### 5. Test fixture scope must match commit behaviour

If your repository `save()` calls `db.commit()`, you cannot use transaction-rollback for test
isolation — the commit escapes the savepoint. Design your fixture cleanup strategy (truncation)
to match how your production code uses the session.

### 6. Alembic `autogenerate` requires all ORM models to be imported

`alembic/env.py` must import the `Base` (and transitively all mapped classes) before
`target_metadata = Base.metadata` is evaluated. Putting all ORM models in a single
`orm/models.py` module makes this import straightforward and avoids missing-table surprises.

---

## Verification

```bash
# Unit tests (no database required)
pytest tests/unit/ -v
# → 39 passed in 0.21s

# Integration + E2E tests (requires medistock_test PostgreSQL database)
pytest tests/integration/ tests/e2e/ -v
# → 64 passed in 2.93s

# Full suite
pytest
# → 103 passed

# Local server
uvicorn medistock.interfaces.api.main:app --reload
# Swagger UI: http://127.0.0.1:8000/docs

# Docker Compose (app + PostgreSQL, runs migrations automatically)
docker compose up --build
```

## Repository

**GitHub:** https://github.com/naara011100/Capstone_Projekt_MediStock
**Branch:** `main`
**Latest tag:** —  *(tag `v1.0.0` to trigger the Release + CD pipeline)*
