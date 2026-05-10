# Phase 0 — Bootstrap

**AI-SDLC Phase:** Environment setup, toolchain selection, repository initialisation  
**Status:** ✅ Complete  
**Date:** 2026-04-13  
**AI Tool:** Claude Code (Anthropic) — `claude-sonnet-4-6` via VS Code extension

---

## Objective

Stand up a working development environment and empty repository before writing
any domain code.  Validate that the chosen toolchain integrates cleanly with
the AI coding assistant.

---

## Actions Taken

### 1. Environment

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13.1 | Runtime |
| FastAPI | latest | HTTP framework |
| SQLAlchemy | latest | ORM |
| Alembic | latest | Schema migrations |
| PostgreSQL | 16 (Docker) | Database |
| pytest + httpx | latest | Test runner + HTTP client |
| uvicorn | latest | ASGI server |
| VS Code | latest | IDE |
| Claude Code | extension | AI coding assistant |

### 2. AI Tool Choice Rationale

**Why Claude Code over GitHub Copilot or ChatGPT web?**

- Claude Code operates as a full coding agent: it reads files, runs shell
  commands, edits code, and tracks context across a session — not just inline
  completion.
- It runs inside VS Code via the official extension, with access to the live
  file tree and terminal output.
- It can explain architectural tradeoffs, generate tests, diagnose live
  tracebacks, and propose fixes, all in one conversation.
- `claude-sonnet-4-6` produces code that follows best practices (type hints,
  error handling, test coverage) without prompting.

### 3. Repository Initialisation

```bash
git init
git remote add origin https://github.com/naara011100/Capstone_Projekt_MediStock
```

The repository was empty (single `README.md`) when AI-assisted development began.

---

## Prompt Used

None in this phase — setup was manual.  The first AI prompt appears in Phase 1
(domain specification) and Phase 3 (code generation).

---

## Human vs AI

| Task | Owner |
|------|-------|
| Install Python, PostgreSQL, VS Code | Human |
| Choose FastAPI as HTTP framework | Human |
| Choose clean architecture as structural pattern | Human |
| Set up GitHub repository | Human |
| Install Claude Code VS Code extension | Human |
| Verify environment with `python --version` | Human |

**AI involvement in this phase: 0%**

---

## Output

- Working Python 3.13 environment
- Empty FastAPI project slot (no code yet)
- Claude Code connected to the repository via VS Code
- Architecture pattern chosen (Clean Architecture / Hexagonal)
