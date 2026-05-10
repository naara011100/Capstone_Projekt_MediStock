# Phase 2 — Design

**AI-SDLC Phase:** Architecture decisions, layer design, database schema, API design  
**Status:** ✅ Complete  
**Dates:** 2026-04-13 (architecture), 2026-04-18 (DB design), 2026-05-10 (application layer)  
**AI Tool:** Claude Code — collaborative decision-making; final choices made by developer

---

## Objective

Decide the structure of each layer before generating code, so that prompts
can be written with precision and Claude's output matches the intended design.

---

## Architecture Decision: Clean Architecture

```
┌──────────────────────────────────────────────────┐
│  Interfaces  (FastAPI routers, web UI)            │
│  ┌────────────────────────────────────────────┐  │
│  │  Application  (BookingUseCase,              │  │
│  │               InventoryUseCase)             │  │
│  │  ┌──────────────────────────────────────┐  │  │
│  │  │  Domain  (models, services, ABCs)    │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────┘  │
│  Infrastructure  (SQLAlchemy ORM, repositories)   │
└──────────────────────────────────────────────────┘
```

**Why Clean Architecture?**
The project needed to demonstrate separation of concerns as a capstone.
Clean Architecture gives each layer exactly one reason to change:
- Domain changes when business rules change
- Infrastructure changes when the database changes
- Interfaces change when the API contract changes
- Application layer changes when workflows change

**Dependency rule:** arrows point inward.  Domain knows nothing about FastAPI
or SQLAlchemy.  The domain can be run and tested with plain Python.

---

## Key Design Decisions

### D-001 — All ORM Models in One File

All six SQLAlchemy mapped classes live in `infrastructure/orm/models.py`.

**Reason:** SQLAlchemy resolves relationship strings (e.g.
`relationship("PatientORM")`) at mapper configuration time.  Splitting models
across files creates circular import risks and string-resolution failures.
One file, one `Base`, zero ambiguity.

### D-002 — `object.__new__()` in ORM→Domain Mappers

Every `build_*()` function in `repositories/base.py` bypasses `__post_init__`
by constructing domain objects via `object.__new__()`.

**Reason:** `Appointment.__post_init__` asserts `scheduled_at > utcnow()`.
Any appointment loaded from the database would fail this check.  The guard is
correct for *creation*; it is wrong for *reconstruction from storage*.
`object.__new__()` is the idiomatic bypass pattern for this case.

### D-003 — `safe_commit()` Context Manager

A single `@contextmanager` in `base.py` wraps every `db.commit()` call and
converts `IntegrityError` → `DuplicateEntryError`.

**Reason:** Avoids repeating the try/except/rollback pattern in every `save()`
method across six repositories.  Keeps infrastructure exceptions out of domain
code.

### D-004 — `session.merge()` for Save-or-Update

All `save()` methods call `db.merge(orm_object)` instead of separate `add()`
(insert) and `update()` paths.

**Reason:** Domain objects carry their own UUID from construction. `merge()`
handles INSERT vs UPDATE by primary key transparently.  One code path, no
conditional branching per repository.

**Known limitation discovered in Phase 4:** `merge()` keys on PK only.  A
new domain object with a new UUID but a duplicate email still attempts an
INSERT and hits the unique index.  Fixed by `safe_commit()` wrapping.

### D-005 — `lazy="joined"` on Frequently Accessed Relationships

`AppointmentORM → patient/doctor/room` and `StockItemORM → medication` use
eager loading via `lazy="joined"`.

**Reason:** These relationships are always needed when the entity is returned
to the API layer.  Lazy loading would produce N+1 queries on every list
endpoint.  Eager loading trades one slightly larger query for predictable
performance.

### D-006 — Application Layer as Orchestration Boundary

`BookingUseCase` and `InventoryUseCase` in `application/use_cases.py` sit
between routers and domain services.

**Reason added in Sprint 5:** The `POST /appointments/` endpoint originally
resolved patient/doctor/room IDs to domain objects *inside the router*.  That
is workflow orchestration logic — it belongs in a dedicated layer, not in the
HTTP adapter.  The use case gives a single dependency per router endpoint
instead of three separate repo dependencies, and is the correct extension point
for future concerns (auth checks, audit logging).

### D-007 — Two DI Modules Coexist

`dependencies.py` (in-memory) remains alongside `db_dependencies.py`
(PostgreSQL).

**Reason:** Allows the API to be run locally without a database for rapid
prototyping.  Switching backend requires changing one import line per router.

---

## Database Schema Design

| Table | Key indexes |
|-------|------------|
| `patients` | unique email (`ix_patients_email`) |
| `doctors` | unique email (`ix_doctors_email`) |
| `rooms` | unique name constraint |
| `medications` | unique name constraint |
| `stock_items` | FK to medications (RESTRICT on delete) |
| `appointments` | composite (doctor_id, scheduled_at), (patient_id, scheduled_at) |

Composite indexes on appointments support the time-overlap conflict check
without a full table scan.

---

## API Design

| Resource | Prefix | Verbs |
|----------|--------|-------|
| Patients | `/api/v1/patients` | GET, POST, DELETE (soft) |
| Doctors | `/api/v1/doctors` | GET, POST, DELETE (soft) |
| Rooms | `/api/v1/rooms` | GET, POST, PATCH (availability) |
| Appointments | `/api/v1/appointments` | GET, POST, PATCH (status transitions) |
| Inventory | `/api/v1/inventory` | GET, POST (CRUD + stock ops) |

Status transitions use `PATCH` (partial update) rather than `PUT` (full
replacement) — semantically correct for state machine transitions.

---

## Human vs AI

| Decision | Owner | Rationale |
|----------|-------|-----------|
| Clean Architecture pattern | Human | Deliberate project structure choice |
| Abstract repo interfaces (ABCs) | Human | Defined before any infrastructure code |
| `object.__new__()` pattern | Claude | Proposed after identifying the `__post_init__` hydration problem |
| `session.merge()` for upsert | Claude | Suggested as the idiomatic SQLAlchemy approach |
| `safe_commit()` context manager | Claude | Proposed when diagnosing the 500 error |
| `lazy="joined"` on relationships | Claude | Proposed to avoid N+1 queries |
| Application layer addition | Joint | Developer identified the need; Claude implemented |
| Two DI modules coexisting | Human | Explicit design choice for local dev convenience |
