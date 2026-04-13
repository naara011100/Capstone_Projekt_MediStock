# AI-Assisted Development Log — MediStock

This document records how AI tooling was used during the development of this project,
what was generated, what was written manually, and the reasoning behind key decisions.

---

## Tool Used

**Claude Code** (Anthropic) — CLI/IDE assistant powered by `claude-sonnet-4-6`
Accessed via the VS Code extension, operating directly on the local repository.

---

## Session Overview

**Date:** 2026-04-13
**Starting state:** Empty repository (single `README.md`)
**Ending state:** Fully scaffolded FastAPI project with clean architecture

---

## What Was AI-Generated

### 1. Project Scaffold & Directory Structure

Claude created the full folder tree and all `__init__.py` files in a single pass:

```
medistock/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   └── services.py
└── interfaces/
    ├── __init__.py
    └── api/
        ├── __init__.py
        ├── dependencies.py
        ├── main.py
        └── routers/
            └── __init__.py
```

### 2. Domain Models (`medistock/domain/models/`)

All six domain model files were generated with exact content provided in the prompt:

| File | Domain concept | Notable logic |
|---|---|---|
| [patient.py](medistock/domain/models/patient.py) | `Patient` dataclass | Email/name/DOB validation in `__post_init__` |
| [doctor.py](medistock/domain/models/doctor.py) | `Doctor` dataclass | Specialization + email validation |
| [room.py](medistock/domain/models/room.py) | `Room` dataclass | Capacity validation, availability toggling |
| [medication.py](medistock/domain/models/medication.py) | `Medication` dataclass | Name/unit validation, deactivation |
| [stock_item.py](medistock/domain/models/stock_item.py) | `StockItem` dataclass | `add_stock`, `dispense`, low-stock threshold |
| [appointment.py](medistock/domain/models/appointment.py) | `Appointment` + `AppointmentStatus` enum | Status machine, overlap detection |

### 3. Domain Services (`medistock/domain/services.py`)

Claude generated two abstract repository interfaces and two domain services:

- `AbstractAppointmentRepository` / `AbstractStockRepository` — ABCs defining persistence contracts
- `BookingService` — books appointments, enforces conflict checks (doctor, patient, room)
- `InventoryService` — manages stock add/dispense, exposes low-stock alerts

### 4. Infrastructure — In-Memory Repositories (`medistock/interfaces/api/dependencies.py`)

Claude generated `_InMemoryRepo` and its specialised subclasses as a zero-dependency
persistence layer wired via FastAPI `Depends`. This keeps the domain layer pure while
allowing the API to run without a database.

### 5. FastAPI Routers (`medistock/interfaces/api/routers/`)

The router files were **not** provided verbatim in the prompt — Claude inferred and
authored them based on the domain models and services:

| File | Router(s) | Endpoints |
|---|---|---|
| [patients.py](medistock/interfaces/api/routers/patients.py) | `/api/v1/patients` | POST, GET list, GET by id, DELETE (deactivate) |
| [doctors_rooms.py](medistock/interfaces/api/routers/doctors_rooms.py) | `/api/v1/doctors`, `/api/v1/rooms` | Full CRUD + availability toggle for rooms |
| [appointments.py](medistock/interfaces/api/routers/appointments.py) | `/api/v1/appointments` | Book, GET, confirm, complete, cancel, no-show |
| [inventory.py](medistock/interfaces/api/routers/inventory.py) | `/api/v1/inventory` | Medication CRUD + stock add/dispense/low-stock |

Each router includes inline Pydantic request/response schemas.

### 6. Application Entry Point (`medistock/interfaces/api/main.py`)

Generated verbatim from the prompt. Registers all routers under `/api/v1`, applies
CORS middleware, and exposes a `/health` check endpoint.

### 7. `requirements.txt`

```
fastapi
uvicorn
pydantic[email]
pytest
httpx
```

---

## What We Wrote Manually

| Artifact | Written by |
|---|---|
| Initial project idea and domain design (patients, doctors, rooms, appointments, inventory) | Human |
| Domain model field definitions and business rule logic (validation, state transitions) | Human (provided as exact file content in the prompt) |
| Domain service logic (`BookingService`, `InventoryService`) | Human (provided as exact file content in the prompt) |
| Architecture decision: clean architecture with domain / interfaces separation | Human |
| This `AGENTS.md` document | Human (prompted) / Claude (authored) |

Everything else listed in the sections above was authored by Claude Code.

---

## Key Prompts Used

### Prompt 1 — Full project generation
> "Create a complete FastAPI medistock project with clean architecture. Create all folders,
> `__init__.py` files, and the following files with exact content: [domain models, services,
> dependencies, main.py]. After creating all files, also create a `requirements.txt`. Finally
> run: `pip install -r requirements.txt`"

This single prompt scaffolded the entire project. The domain model and service file contents
were supplied verbatim; the router implementations were left for Claude to infer.

### Prompt 2 — This document
> "Create an AGENTS.md file that documents our AI-assisted development process so far:
> tool used, what was generated, key prompts used, what we wrote manually vs what was
> AI-generated."

---

## Architecture Decisions

### Clean Architecture Layers

```
medistock/
├── domain/          ← pure Python, no framework dependencies
│   ├── models/      ← dataclasses with business rules
│   └── services.py  ← use-case logic + abstract repository contracts
└── interfaces/
    └── api/         ← FastAPI layer; adapts HTTP to domain calls
        ├── dependencies.py   ← DI wiring (in-memory repos for now)
        ├── main.py           ← app factory
        └── routers/          ← one file per bounded context
```

The domain layer has zero knowledge of FastAPI, Pydantic, or any persistence technology.
This makes it independently testable and replaceable.

### In-Memory Repositories

The current persistence layer is intentional — it lets the API run and be tested with no
database setup. Swapping to SQLAlchemy/PostgreSQL only requires implementing the abstract
repository interfaces; no domain or service code changes.

### Pydantic Schemas Co-located with Routers

Request/response schemas live inside each router module rather than a shared `schemas/`
directory. For a project of this size this avoids premature abstraction; if the schema
surface grows significantly, extraction into a dedicated package is the natural next step.

---

## Verification

After generation, Claude ran a smoke test to confirm all imports resolved and routes
registered correctly:

```
python -c "from medistock.interfaces.api.main import app; print(len(app.routes), 'routes')"
# → 32 routes registered
```

To start the server locally:

```bash
uvicorn medistock.interfaces.api.main:app --reload
# Docs available at http://127.0.0.1:8000/docs
```
