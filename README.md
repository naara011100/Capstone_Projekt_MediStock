# MediStock

[![CI](https://github.com/naara011100/Capstone_Projekt_MediStock/actions/workflows/ci.yml/badge.svg)](https://github.com/naara011100/Capstone_Projekt_MediStock/actions/workflows/ci.yml)
[![API Health](https://img.shields.io/website?url=https%3A%2F%2Fmedistock.onrender.com%2Fhealth&label=API&up_message=online&down_message=offline)](https://medistock.onrender.com/health)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/naara011100/Capstone_Projekt_MediStock/pkgs/container/medistock)
[![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)

REST-API zur Krankenhausverwaltung, entwickelt mit **FastAPI**, **SQLAlchemy** und **PostgreSQL**.  
Verwaltet Patientenregistrierung, Arztplanung, Terminbuchung und Medikamentenbestand.

---

## Live-System

| Bereich | URL |
|---------|-----|
| Web-Oberfläche | https://medistock.onrender.com/ui |
| API-Dokumentation (Swagger) | https://medistock.onrender.com/docs |
| Statusprüfung | https://medistock.onrender.com/health |

---

## Health-Endpunkt

```
GET /health
```

Gibt den aktuellen Servicestatus zurück. Keine Authentifizierung erforderlich.

**Antwort `200 OK`:**

```json
{
  "status": "ok",
  "service": "medistock"
}
```

Dieser Endpunkt eignet sich zur Überprüfung der API-Erreichbarkeit sowie zur Anbindung an ein Uptime-Monitoring.

```bash
curl https://medistock.onrender.com/health
```

---

## Architektur

Vierschichtige Clean Architecture — die Domänenlogik hat keinerlei Kenntnis von FastAPI oder SQLAlchemy.

```
Interfaces  →  Application  →  Domain  →  Infrastructure
(FastAPI)      (UseCases)     (Models)    (SQLAlchemy / PostgreSQL)
```

Vollständiges Architekturdiagramm und Designentscheidungen: [docs/PROJECT.md](docs/PROJECT.md)

---

## API-Übersicht

| Ressource | Basispfad | Operationen |
|-----------|-----------|-------------|
| Patienten | `/api/v1/patients/` | auflisten, erstellen, abrufen, deaktivieren |
| Ärzte | `/api/v1/doctors/` | auflisten, erstellen, abrufen, deaktivieren |
| Räume | `/api/v1/rooms/` | auflisten, erstellen, abrufen, Verfügbarkeit ändern |
| Termine | `/api/v1/appointments/` | auflisten, buchen, abrufen, bestätigen, abschließen, stornieren, nicht erschienen |
| Medikamente | `/api/v1/inventory/medications` | auflisten, erstellen, abrufen |
| Lagerbestand | `/api/v1/inventory/stock` | auflisten, Niedrigbestand-Warnungen, hinzufügen, ausgeben |

Interaktive Dokumentation verfügbar unter `/docs` (Swagger UI) und `/redoc`.

---

## Schnellstart

### Lokal (mit laufendem PostgreSQL)

```bash
# 1. Repository klonen
git clone https://github.com/naara011100/Capstone_Projekt_MediStock.git
cd Capstone_Projekt_MediStock

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Datenbank konfigurieren
cp .env.example .env          # DATABASE_URL anpassen

# 4. Datenbankmigrationen ausführen
alembic upgrade head

# 5. Server starten
uvicorn medistock.interfaces.api.main:app --reload
# → http://127.0.0.1:8000/ui
```

### Docker Compose (App + PostgreSQL, keine Konfiguration nötig)

```bash
docker compose up --build
# → http://localhost:8000/ui
```

Datenbankmigrationen werden beim Containerstart automatisch über `entrypoint.sh` ausgeführt.

---

## Tests

```bash
# Unit-Tests — keine Datenbank erforderlich (wird auch in CI ausgeführt)
pytest tests/unit/ -v

# Vollständige Testsuite — erfordert medistock_test PostgreSQL-Datenbank
pytest
```

103 Tests in den Schichten Unit, Integration und End-to-End.

---

## Technologie-Stack

| Schicht | Technologie |
|---------|-------------|
| HTTP-Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Datenbank | PostgreSQL 16 |
| Migrationen | Alembic |
| Validierung | Pydantic v2 |
| Container | Docker (python:3.12-slim, non-root) |
| CI/CD | GitHub Actions |
| Image-Registry | GitHub Container Registry (GHCR) |
| Hosting | Render |

---
## Was haben wir selbst gemacht und was hat Claude Code generiert?
Wir haben den Use Case, die Entitäten und alle Business Rules selbst definiert. Claude Code hat daraus Boilerplate, Tests, CI/CD und Infrastruktur-Code generiert. Alle Architekurentscheidungen (Clean Architecture, Repository Pattern, TDD) haben wir gemeinsam getroffen und bewusst verantwortet.

## Repository

**GitHub:** https://github.com/naara011100/Capstone_Projekt_MediStock  
**KI-Entwicklungsdokumentation:** [AGENTS.md](AGENTS.md)  
**Use-Case-Spezifikationen:** [docs/specs/](docs/specs/)
