# AGENTS.md — MediStock AI-SDLC Workflow

This file is the **workflow router** for the MediStock capstone project.
It documents how Claude Code was used as an active coding agent throughout the
full software development lifecycle — from blank repository to deployed
application — using a structured AI-SDLC process.

---

## AI Tool

| Property | Value |
|----------|-------|
| Tool | **Claude Code** (Anthropic) |
| Model | `claude-sonnet-4-6` |
| Interface | VS Code extension, operating directly on the local repository |
| Capabilities used | File read/write, shell commands, test execution, traceback analysis |

Claude Code is a coding *agent* — it does not just suggest completions.  It
reads the full project, runs commands, modifies files, and tracks context
across a session.  This distinction matters: every output below came from a
conversation that included live file content, not from a standalone prompt.

---

## AI-SDLC Phases

The project followed a six-phase AI-assisted SDLC.  Each phase has a dedicated
skill file with the full prompt, outputs, and Human vs AI breakdown.

| Phase | Skill File | What happened | Status |
|-------|-----------|---------------|--------|
| **0 — Bootstrap** | [skills/ai-sdlc-0-bootstrap.md](skills/ai-sdlc-0-bootstrap.md) | Environment setup, tool choice, repository init | ✅ Complete |
| **1 — Specify** | [skills/ai-sdlc-1-specify.md](skills/ai-sdlc-1-specify.md) | Domain models, business rules, use case definition — human-authored | ✅ Complete |
| **2 — Design** | [skills/ai-sdlc-2-design.md](skills/ai-sdlc-2-design.md) | Clean architecture decisions, DB schema, API design | ✅ Complete |
| **3 — Develop** | [skills/ai-sdlc-3-develop.md](skills/ai-sdlc-3-develop.md) | All code generation: routers, ORM, repos, use cases, web UI | ✅ Complete |
| **4 — Validate** | [skills/ai-sdlc-4-validate.md](skills/ai-sdlc-4-validate.md) | 103 tests (unit/integration/e2e), bug fix (500 → 409) | ✅ Complete |
| **5 — Deploy** | [skills/ai-sdlc-5-deploy.md](skills/ai-sdlc-5-deploy.md) | Dockerfile, docker-compose, CI/CD pipelines, git hygiene | ✅ Complete |

---

## Full Prompt Log

Every prompt sent to Claude Code that produced a project artifact:

| # | Phase | Prompt (abbreviated) | Key Output |
|---|-------|---------------------|-----------|
| 1 | Develop | Full project scaffold with exact domain model content | Directory tree, all 4 routers, in-memory DI, requirements.txt |
| 2 | Develop | Create AGENTS.md | Initial AI development log |
| 3 | Develop | SQLAlchemy infrastructure layer + Alembic setup | ORM models, 6 repos, db_dependencies.py, alembic files |
| 4 | Develop | .env + dotenv + switch routers to PostgreSQL + run migrations | load_dotenv wiring, DB tables created via Alembic |
| 5 | Validate | Fix 500 on POST /api/v1/doctors/ | `safe_commit`, `DuplicateEntryError`, 409 responses |
| 6 | Validate | Complete test suite (unit + integration + e2e) | 103 tests, pytest.ini, conftest fixtures |
| 7 | Deploy | CI/CD + Dockerfile + docker-compose | 3 workflow files, Dockerfile, entrypoint.sh |
| 8 | Deploy | Git setup + .gitignore + push commands | .gitignore, cleaned 56 tracked cache files, .env removed |
| 9 | Deploy | Commit and push to GitHub | Verified clean tree, pushed to origin/main |
| 10 | Develop | Update AGENTS.md with full session log | Session 3 documentation |
| 11 | Develop | Minimal web UI at /ui with 4 tabs | index.html, StaticFiles mount, /ui route |
| 12 | Develop | Application layer (use cases) + wire into routers | use_cases.py, updated appointments + inventory routers |
| 13 | Develop | Add application layer docs + use case specs | docs/PROJECT.md, UC-001, UC-002, docs/TASKS.md |
| 14 | Develop | AI-SDLC restructure: skills/ folder + new AGENTS.md | skills/*.md, AGENTS.md (this file), scripts/setup-skills.sh |
| 15 | Deploy | Commit and push all current changes to GitHub | Verified clean tree; confirmed .env not tracked; pushed |
| 16 | Validate | CI workflow failing on unit tests — check logs and fix | Identified `--no-cache-dir` + `cache: "pip"` contradiction; removed flag from ci.yml |
| 17 | Validate | Appointment booking returns 500 — debug and fix | Diagnosed `TypeError` from timezone-aware vs naive datetime comparison; fixed appointment.py + index.html |
| 18 | Deploy | Create and push git tag v1.0.0 to trigger Release + CD | Tag pushed; Release (GHCR) and CD (Render) pipelines triggered |
| 19 | Deploy | CD workflow failing — what secret does it expect? | Read cd.yml; identified required secret: `RENDER_DEPLOY_HOOK_URL` |
| 20 | Deploy | git tag v1.0.2 + git push origin v1.0.2 | Tag pushed after Render secret was configured |
| 21 | Develop | Add Mermaid architecture diagram to docs/PROJECT.md | Replaced ASCII box diagram with colour-coded Mermaid `graph TD` |
| 22 | Develop | Document /health endpoint in README.md + live API badge | Full README with CI badge, shields.io health badge, endpoint docs, quick-start |
| 23 | Develop | Update AGENTS.md with last session prompts | This entry — prompts 15–23 added, lessons 7–8 added |

---

## Human vs AI — Summary Table

### Human-Authored (no AI involvement)

| Artifact | Why it had to be human |
|----------|----------------------|
| All six domain model class definitions | Core business logic; defines the problem |
| Field types, validation rules, business methods | Domain expertise; not inferable from requirements |
| `BookingService` — conflict detection algorithm | Business rule: how overlapping appointments are detected |
| `InventoryService` — stock management rules | Business rule: upsert semantics, understock prevention |
| Abstract repository contracts (`ABCs`) | Architecture decision: what persistence must guarantee |
| Clean Architecture as structural pattern | Deliberate project structure choice |
| Database credentials (`.env`) | Security |
| Choice of Render for cloud deployment | Infrastructure decision |
| Decision to use PostgreSQL as database | Infrastructure decision |

### AI-Generated (Claude Code, from prompt context)

| Artifact | How Claude derived it |
|----------|----------------------|
| All 4 FastAPI routers + Pydantic schemas | Inferred from domain models and service method signatures |
| SQLAlchemy ORM models (all 6 entities) | Derived from domain model fields and relationship structure |
| All 6 `SQLAlchemy*Repository` implementations | Derived from abstract repository contracts |
| `object.__new__()` mapper pattern | Identified that `__post_init__` guards fail for DB hydration |
| `safe_commit()` context manager | Designed after diagnosing live `IntegrityError` traceback |
| `DuplicateEntryError` exception hierarchy | Consequence of `safe_commit` design |
| 103 tests across unit / integration / e2e | Designed from API surface, domain rules, and edge cases |
| Test isolation via table truncation | Identified incompatibility of rollback with `db.commit()` in saves |
| Two-stage Dockerfile | Standard best-practice applied to project structure |
| `entrypoint.sh` with migrations-on-start | Idiomatic Alembic pattern for single-container deployments |
| CI/CD workflow YAML files (3) | Derived from toolchain (pytest, Docker, Render deploy hook) |
| `.gitignore` | Standard Python template |
| Web UI (HTML/CSS/JS) | Designed from API endpoint signatures |
| `BookingUseCase` + `InventoryUseCase` | Derived from workflow in `book_appointment` router endpoint |
| `docs/PROJECT.md` + use case specs | Synthesised from all project artefacts |
| `skills/` files (this restructure) | Synthesised from full session history |
| CI fix: remove `--no-cache-dir` from ci.yml | Diagnosed contradiction between `cache: "pip"` and `--no-cache-dir` by reading GHA post-step failure |
| Timezone fix: `appointment.py` + `index.html` | Traced 500 → `TypeError` from aware-vs-naive datetime comparison; proposed two-layer fix |
| Mermaid architecture diagram | Generated from layer descriptions in docs/PROJECT.md |
| Full README with badges and endpoint docs | Derived from project structure, CI workflow names, and `/health` route |

---

## Architecture Decisions

See [docs/PROJECT.md](docs/PROJECT.md) for the full architecture document.

Key decisions at a glance:

| Decision | Rationale |
|----------|-----------|
| Clean Architecture (4 layers) | Separation of concerns; domain testable without DB or HTTP |
| `object.__new__()` for DB hydration | `__post_init__` guards are write-time rules, not read-time invariants |
| `safe_commit()` + `DuplicateEntryError` | Single place to handle `IntegrityError`; 409 ≠ 422 |
| `lazy="joined"` on always-needed relationships | Eliminates N+1 queries on list endpoints |
| Application layer for orchestration | ID-resolution logic belongs above the HTTP adapter |
| Truncation (not rollback) for test isolation | `db.commit()` in saves is incompatible with savepoint rollback |
| Migrations-on-container-start | Idempotent, zero-downtime safe for Alembic's incremental model |

---

## Project Status

**Lifecycle phase: DEPLOYED** (as of 2026-05-10)

```bash
# All 39 unit tests (no DB required)
pytest tests/unit/ -v          # → 39 passed in 0.12s

# Full suite (requires medistock_test DB)
pytest                         # → 103 passed

# Local server
uvicorn medistock.interfaces.api.main:app --reload
# → http://127.0.0.1:8000/ui       (web UI)
# → http://127.0.0.1:8000/docs     (Swagger)

# Docker Compose (full stack)
docker compose up --build
```

**Repository:** https://github.com/naara011100/Capstone_Projekt_MediStock  
**Branch:** `main`  
**Latest tag: `v1.0.2`** — triggers the Release (GHCR Docker push) + CD (Render deploy) pipelines.

---

## Lessons Learned

Detailed per-phase lessons are in the skill files.  Top six:

1. **`session.merge()` is not a unique-aware upsert.** It keys on PK only.
   Always wrap `save()` with a guard for `IntegrityError` → 409.

2. **`__post_init__` guards are write-time, not read-time invariants.**
   Use `object.__new__()` when reconstructing domain objects from storage.

3. **`.gitignore` does not retroactively untrack committed files.**
   Use `git rm --cached` after the fact.

4. **Commit-inside-save is incompatible with rollback-based test isolation.**
   Design fixtures to truncate tables, not rollback transactions.

5. **Distinguish 409 (conflict) from 422 (invalid) at the HTTP layer.**
   These are different failure modes and should give consumers different
   signals.

6. **The AI is most useful when the domain is already specified.**
   Claude generated correct routers, ORM, and tests because the domain
   models and ABCs were precise.  Vague specs produce vague code.

7. **`cache: "pip"` and `--no-cache-dir` are mutually exclusive in GitHub Actions.**
   `actions/setup-python` saves pip's download cache in a post-step.
   `pip install --no-cache-dir` prevents pip from writing to that directory,
   leaving it empty and causing the post-step to fail — even when all tests
   pass.  Use one or the other, not both.

8. **`datetime.utcnow()` (naive) vs timezone-aware datetimes raises `TypeError`, not `ValueError`.**
   The browser's `toISOString()` appends a `Z` suffix; Pydantic v2 parses this
   as a timezone-aware `datetime`.  Comparing it against `datetime.utcnow()`
   (naive) raises `TypeError`, which the router's `except ValueError` does not
   catch — producing an unhandled HTTP 500.  Fix at both layers: normalise to
   naive UTC in the domain model's `__post_init__`, and stop calling
   `toISOString()` in the frontend.
