# Phase 1 — Specify

**AI-SDLC Phase:** Requirements, domain model specification, use case definition  
**Status:** ✅ Complete  
**Date:** 2026-04-13  
**AI Tool:** Claude Code — used to scaffold, but specification content was human-authored

---

## Objective

Define the hospital domain model and business rules precisely enough that the
AI can generate correct infrastructure and API code from them in Phase 3.

---

## Domain Entities Specified (Human-Authored)

Every field, type, validation rule, and business method below was written by
the developer — not inferred by Claude.  These were supplied as exact file
content in the first prompt.

### Patient
```
Fields:  id (UUID), first_name, last_name, date_of_birth, email, phone,
         is_active, created_at
Rules:   • first_name, last_name must be non-empty
         • email must contain '@'
         • date_of_birth must be in the past
Methods: full_name (property), deactivate()
```

### Doctor
```
Fields:  id (UUID), first_name, last_name, specialization, email, phone,
         is_active, created_at
Rules:   • All string fields must be non-empty
         • email must contain '@'
Methods: full_name → "Dr. {first} {last}", deactivate()
```

### Room
```
Fields:  id (UUID), name, floor (int), capacity (int), is_available, created_at
Rules:   • name must be non-empty
         • capacity must be positive
Methods: mark_available(), mark_unavailable()
```

### Medication
```
Fields:  id (UUID), name, description, unit, is_active, created_at
Rules:   • name and unit must be non-empty
Methods: deactivate()
```

### StockItem
```
Fields:  id (UUID), medication (Medication), quantity (int), location,
         low_stock_threshold (default 10), created_at, updated_at
Constants: LOW_STOCK_THRESHOLD = 10
Rules:   • quantity cannot be negative at initialisation
         • location must be non-empty
Methods: add_stock(amount), dispense(amount)
         is_low (property), is_out_of_stock (property)
```

### Appointment
```
Fields:  id (UUID), patient, doctor, room, scheduled_at (datetime),
         duration_minutes (int), status (enum), notes, created_at, updated_at
Status:  SCHEDULED → CONFIRMED → COMPLETED
         SCHEDULED/CONFIRMED → CANCELLED / NO_SHOW
Rules:   • scheduled_at must be in the future (UTC)
         • duration_minutes must be positive
Methods: end_time (property), confirm(), complete(), cancel(), mark_no_show()
         overlaps_with(other) → bool
```

---

## Use Cases Identified

### UC-001 — Book Appointment
An actor selects a patient, doctor, room, and time slot.  The system must:
- Verify all three entities exist
- Reject bookings in the past
- Detect time-slot conflicts for doctor, patient, and room
- Persist the appointment with status SCHEDULED

Full spec: [docs/specs/UC-001-book-appointment.md](../docs/specs/UC-001-book-appointment.md)

### UC-002 — Manage Medication Inventory
An actor adds stock deliveries and records dispensing.  The system must:
- Upsert stock entries (one per medication)
- Prevent stock from going below zero
- Surface low-stock alerts (quantity ≤ threshold)

Full spec: [docs/specs/UC-002-manage-inventory.md](../docs/specs/UC-002-manage-inventory.md)

---

## Abstract Repository Contracts (Human-Authored)

Two abstract base classes defined the persistence contract before any
infrastructure code existed:

```python
class AbstractAppointmentRepository(ABC):
    save, get_by_id, list_all,
    list_by_doctor, list_by_patient, list_by_status

class AbstractStockRepository(ABC):
    save, get_by_id, get_by_medication,
    list_all, list_low_stock
```

These ABCs live in `domain/services.py` — no imports from SQLAlchemy.

---

## Prompt Used

> "Create a complete FastAPI medistock project with clean architecture.
> Create all folders, `__init__.py` files, and the following files with
> exact content: [all six domain model files and services.py]…"

The domain model content was supplied verbatim in the prompt body.
Claude's role in this phase was scaffolding (directories, `__init__.py`
files) — not domain design.

---

## Human vs AI

| Task | Owner |
|------|-------|
| All six domain model class definitions | Human |
| Field types, validation rules, business methods | Human |
| `BookingService` conflict-detection algorithm | Human |
| `InventoryService` stock management logic | Human |
| Abstract repository contracts (ABCs) | Human |
| Directory scaffolding and `__init__.py` files | Claude |

**Human involvement: ~95% (all domain logic)**
