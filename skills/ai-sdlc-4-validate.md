# Phase 4 — Validate

**AI-SDLC Phase:** Testing, bug discovery, and verification  
**Status:** ✅ Complete  
**Date:** 2026-04-19  
**AI Tool:** Claude Code — designed and generated the full test suite

---

## Objective

Validate that the implementation is correct at three levels — unit, integration,
and end-to-end — and fix any defects found during testing.

---

## Test Suite

**Prompt:**
> "Create a complete test suite:
> 1. Unit tests in tests/unit/ — test BookingService and InventoryService
>    with mocked repositories (no database needed)
> 2. Integration tests in tests/integration/ — test the FastAPI routes using
>    TestClient and a test PostgreSQL database
> 3. E2E tests in tests/e2e/ — test full workflows
> Also create a pytest.ini config file and make sure all tests pass."

### Test Inventory

| File | Count | Strategy |
|------|-------|---------|
| `tests/unit/test_booking_service.py` | 20 | `MagicMock` repo, no DB |
| `tests/unit/test_inventory_service.py` | 19 | `MagicMock` repo, no DB |
| `tests/integration/test_patients.py` | 10 | TestClient + real DB |
| `tests/integration/test_doctors.py` | 12 | TestClient + real DB (includes rooms) |
| `tests/integration/test_appointments.py` | 15 | Full status-transition coverage |
| `tests/integration/test_inventory.py` | 15 | Medication CRUD + stock lifecycle |
| `tests/e2e/test_workflows.py` | 7 | Full HTTP journeys |
| **Total** | **103** | |

**Result: 103 passed, 0 failed**

---

## Test Architecture Decisions

### Decision T-001 — Session-scoped Engine, Function-scoped Session

```python
@pytest.fixture(scope="session")
def test_engine():    # creates tables once per test run
    ...

@pytest.fixture()
def db_session(test_engine):  # new session per test
    ...

@pytest.fixture()
def client(db_session, test_engine):  # TestClient + cleanup
    ...
```

**Why:** Creating the schema once per session (not per test) keeps the suite
fast.  A new SQLAlchemy `Session` per test prevents state leakage between tests.

### Decision T-002 — Truncation Not Transaction Rollback

After each test the `client` fixture truncates all tables in FK-safe reverse
order:

```python
for table in reversed(Base.metadata.sorted_tables):
    conn.execute(table.delete())
conn.commit()
```

**Why:** `safe_commit()` in production code calls `db.commit()` inside every
`save()`.  A `db.rollback()` at test teardown cannot undo committed rows.
Truncation is the only reliable isolation strategy when the SUT commits.

### Decision T-003 — Auto-Create Test Database

`conftest.py` connects to the `postgres` maintenance database with AUTOCOMMIT
and runs `CREATE DATABASE medistock_test` if it does not already exist.

**Why:** Eliminates a manual setup step.  Tests are self-contained — any
developer with a local PostgreSQL instance can run them immediately.

### Decision T-004 — Unit Tests Need No Database

Unit tests import `BookingService` and `InventoryService` directly with
`MagicMock` repositories.  They never request `client` or `test_engine`.

**Why:** Keeps the unit test run to < 0.2 seconds.  CI runs only `tests/unit/`
so no database is needed in GitHub Actions.

---

## Bug Discovered and Fixed in This Phase

### Bug: 500 Internal Server Error on `POST /api/v1/doctors/`

**Discovery method:** Ran a local uvicorn server and sent two identical POST
requests for the same doctor email.  Second request returned HTTP 500.

**Traceback (abbreviated):**
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation)
  duplicate key value violates unique constraint "ix_doctors_email"
```

**Root cause:** `session.merge()` keys on the primary key (UUID) only.  Every
new `Doctor()` gets a fresh `uuid4`, so `merge()` always attempts an INSERT —
even when an email already exists in the table.

**Fix applied:**

1. `repositories/base.py` — added `DuplicateEntryError` and `safe_commit()`:
```python
@contextmanager
def safe_commit(db: Session):
    try:
        yield
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEntryError(str(exc.orig)) from exc
```

2. All six `save()` methods wrapped with `with safe_commit(self._db):`

3. All six router create-endpoints got a separate `except DuplicateEntryError`
   block returning **HTTP 409 Conflict**.

**HTTP status code reasoning:**
- 422 = domain validation failed (request data was semantically invalid)
- 409 = DB constraint conflict (request was valid but conflicts with existing data)
- These are distinct failure modes and deserve distinct status codes.

---

## Verification Commands

```bash
# Unit tests only (no database required — used in CI)
pytest tests/unit/ -v
# → 39 passed in 0.12s

# Integration + E2E (requires medistock_test database)
pytest tests/integration/ tests/e2e/ -v
# → 64 passed

# Full suite
pytest
# → 103 passed
```

---

## Human vs AI

| Task | Owner |
|------|-------|
| Decision to test at three levels | Human |
| Test isolation strategy (truncation vs rollback) | Claude |
| All 103 test cases | Claude |
| Bug discovery (manual reproduction) | Human + Claude (traceback analysis) |
| Root cause diagnosis (merge/PK/unique) | Claude |
| Fix design (safe_commit + 409) | Claude |
| Verification that 422 ≠ 409 | Joint |
