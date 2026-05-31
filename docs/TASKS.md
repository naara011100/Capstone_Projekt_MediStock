# MediStock — Projektaufgaben

**Aktueller Lebenszyklusstand: 🚀 DEPLOYED**

Zuletzt aktualisiert: 2026-05-10

---

## Abgeschlossen

### Sprint 1 — Domäne + API-Grundgerüst (2026-04-13)
- [x] Domänenmodelle definieren: Patient, Doctor, Room, Appointment, Medication, StockItem
- [x] `BookingService` mit Konflikterkennung implementieren
- [x] `InventoryService` mit Niedrigbestand-Warnungen implementieren
- [x] FastAPI-App mit fünf Routern anlegen (patients, doctors, rooms, appointments, inventory)
- [x] In-Memory-Repository-Implementierungen für lokale Entwicklung

### Sprint 2 — Datenbankintegration (2026-04-18)
- [x] SQLAlchemy ORM-Modelle für alle sechs Entitäten
- [x] Konkrete Repository-Implementierungen (`SQLAlchemy*Repository`)
- [x] Alembic-Migrations-Setup + initiale Schema-Migration
- [x] `python-dotenv`-Integration; `.env` für lokale DB-Zugangsdaten
- [x] Alle Router von In-Memory auf PostgreSQL-Repositories umstellen
- [x] `safe_commit()`-Context-Manager + `DuplicateEntryError` → HTTP 409

### Sprint 3 — Qualität & Deployment (2026-04-19)
- [x] 500-Fehler bei doppelter E-Mail auf POST /api/v1/doctors/ behoben
- [x] 103-Test-Suite: Unit (gemockte Services), Integration (TestClient + echte DB), E2E (Workflows)
- [x] GitHub Actions CI-Workflow (Unit-Tests bei push/PR)
- [x] GitHub Actions Release-Workflow (Docker-Image → GHCR bei Version-Tag)
- [x] GitHub Actions CD-Workflow (Render-Deploy-Hook nach Release)
- [x] Zweistufiges Dockerfile (`python:3.12-slim`, Non-Root-User, `entrypoint.sh`)
- [x] `docker-compose.yml` mit postgres:16-alpine + Healthcheck
- [x] `.gitignore` für Python + versehentlich getrackte Secrets aus Git-Historie entfernt

### Sprint 4 — Web-Oberfläche (2026-05-10)
- [x] Single-Page Vanilla-JS-UI unter `medistock/interfaces/web/static/index.html`
- [x] Vier Tabs: Patienten, Ärzte (+ Räume), Termine, Lagerbestand
- [x] FastAPI Static-File-Mount + `/ui`-Route + Weiterleitung von `/`
- [x] Formulare an alle bestehenden API-Endpunkte mit korrekten Feldnamen angebunden
- [x] Toast-Benachrichtigungen, Status-Badges, mobilfreundliches Grid

### Sprint 5 — Anwendungsschicht + Dokumentation (2026-05-10)
- [x] `medistock/application/use_cases.py` — `BookingUseCase`, `InventoryUseCase`
- [x] Use-Cases in `appointments`- und `inventory`-Router eingebunden
- [x] `get_booking_use_case` und `get_inventory_use_case` zu `db_dependencies.py` hinzugefügt
- [x] `docs/PROJECT.md` — Architekturübersicht und Designentscheidungen
- [x] `docs/specs/UC-001-book-appointment.md` — vollständige Use-Case-Spezifikation
- [x] `docs/specs/UC-002-manage-inventory.md` — vollständige Use-Case-Spezifikation
- [x] `docs/TASKS.md` — diese Datei

### Sprint 6 — KI-SDLC-Dokumentation (2026-05-10)
- [x] `skills/ai-sdlc-0-bootstrap.md` — Umgebungs-Setup-Phase
- [x] `skills/ai-sdlc-1-specify.md` — Domänen-Spezifikations-Phase
- [x] `skills/ai-sdlc-2-design.md` — Architektur-Design-Phase
- [x] `skills/ai-sdlc-3-develop.md` — Code-Generierungs-Phase
- [x] `skills/ai-sdlc-4-validate.md` — Test- und Bugfix-Phase
- [x] `skills/ai-sdlc-5-deploy.md` — Deployment- und CI/CD-Phase
- [x] `AGENTS.md` als KI-SDLC-Workflow-Router umstrukturiert
- [x] `scripts/setup-skills.sh` — Symlink-Hilfsskript für `.claude/` und `.agents/`

---

## Backlog

### Authentifizierung & Autorisierung
- [ ] JWT-basierte Authentifizierung (Login-Endpunkt, Token-Validierungs-Middleware)
- [ ] Rollenbasierte Zugriffskontrolle: Admin, Doctor, Receptionist, Pharmacist
- [ ] Schreibendpunkte schützen; öffentliches Lesen eigener Termine erlauben

### Patientenportal
- [ ] Patienten-Selbstregistrierung und Self-Service-Terminansicht
- [ ] E-Mail-Bestätigung bei Terminbuchung

### Lagerverwaltungserweiterungen
- [ ] Nachbestellschwelle pro Medikament konfigurierbar (derzeit fest auf 10 kodiert)
- [ ] Verfallsdatum-Tracking für Lagerchargen
- [ ] Automatische E-Mail-/Webhook-Benachrichtigung bei Niedrigbestand

### Betrieb
- [ ] Paginierung auf allen Listen-Endpunkten (`?page=&size=`)
- [ ] Strukturiertes Logging mit Request-ID-Korrelation
- [ ] Prometheus-Metriken-Endpunkt (`/metrics`)
- [ ] Datenbank-Read-Replica-Unterstützung für aufwendige Listenabfragen

### Entwicklererfahrung
- [ ] OpenAPI-Client-Generierung für Frontend-Nutzung
- [ ] Seed-Skript für Demo-Daten (`scripts/seed.py`)
- [ ] Lokales Docker-Compose-Dev-Profil mit Hot-Reload
