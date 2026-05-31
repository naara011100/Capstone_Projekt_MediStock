# AGENTS.md — MediStock KI-SDLC-Workflow

Diese Datei ist der **Workflow-Router** für das MediStock-Capstone-Projekt.
Sie dokumentiert, wie Claude Code als aktiver Coding-Agent während des gesamten
Software-Entwicklungslebenszyklus eingesetzt wurde — vom leeren Repository bis zur
deployten Anwendung — unter Verwendung eines strukturierten KI-SDLC-Prozesses.

---

## KI-Werkzeug

| Eigenschaft | Wert |
|-------------|------|
| Werkzeug | **Claude Code** (Anthropic) |
| Modell | `claude-sonnet-4-6` |
| Schnittstelle | VS Code Extension, direkt auf dem lokalen Repository arbeitend |
| Genutzte Fähigkeiten | Dateien lesen/schreiben, Shell-Befehle, Testausführung, Traceback-Analyse |

Claude Code ist ein Coding-*Agent* — er schlägt nicht nur Vervollständigungen vor. Er
liest das gesamte Projekt, führt Befehle aus, ändert Dateien und verfolgt den Kontext
über eine Session. Dieser Unterschied ist entscheidend: jede Ausgabe unten entstammt
einem Gespräch, das live Dateiinhalte einschloss — nicht einem isolierten Prompt.

---

## KI-SDLC-Phasen

Das Projekt folgte einem sechsphasigen KI-unterstützten SDLC. Jede Phase hat eine
eigene Skill-Datei mit dem vollständigen Prompt, den Ausgaben und der Mensch-vs.-KI-Aufteilung.

| Phase | Skill-Datei | Was passierte | Status |
|-------|-------------|---------------|--------|
| **0 — Bootstrap** | [skills/ai-sdlc-0-bootstrap.md](skills/ai-sdlc-0-bootstrap.md) | Umgebungs-Setup, Werkzeugwahl, Repository-Initialisierung | ✅ Abgeschlossen |
| **1 — Specify** | [skills/ai-sdlc-1-specify.md](skills/ai-sdlc-1-specify.md) | Domänenmodelle, Geschäftsregeln, Use-Case-Definition — menschlich verfasst | ✅ Abgeschlossen |
| **2 — Design** | [skills/ai-sdlc-2-design.md](skills/ai-sdlc-2-design.md) | Clean-Architecture-Entscheidungen, DB-Schema, API-Design | ✅ Abgeschlossen |
| **3 — Develop** | [skills/ai-sdlc-3-develop.md](skills/ai-sdlc-3-develop.md) | Gesamte Code-Generierung: Router, ORM, Repos, Use-Cases, Web-UI | ✅ Abgeschlossen |
| **4 — Validate** | [skills/ai-sdlc-4-validate.md](skills/ai-sdlc-4-validate.md) | 103 Tests (unit/integration/e2e), Bugfix (500 → 409) | ✅ Abgeschlossen |
| **5 — Deploy** | [skills/ai-sdlc-5-deploy.md](skills/ai-sdlc-5-deploy.md) | Dockerfile, docker-compose, CI/CD-Pipelines, Git-Hygiene | ✅ Abgeschlossen |

---

## Vollständiges Prompt-Protokoll

Alle Prompts, die an Claude Code gesendet wurden und ein Projekt-Artefakt erzeugt haben:

| # | Phase | Prompt (gekürzt) | Wichtigste Ausgabe |
|---|-------|------------------|--------------------|
| 1 | Develop | Vollständiges Projektgerüst mit exaktem Domänenmodell-Inhalt | Verzeichnisbaum, alle 4 Router, In-Memory-DI, requirements.txt |
| 2 | Develop | AGENTS.md erstellen | Erstes KI-Entwicklungsprotokoll |
| 3 | Develop | SQLAlchemy-Infrastrukturschicht + Alembic-Setup | ORM-Modelle, 6 Repos, db_dependencies.py, Alembic-Dateien |
| 4 | Develop | .env + dotenv + Router auf PostgreSQL umstellen + Migrationen ausführen | load_dotenv-Verdrahtung, DB-Tabellen via Alembic erstellt |
| 5 | Validate | 500-Fehler auf POST /api/v1/doctors/ beheben | `safe_commit`, `DuplicateEntryError`, 409-Antworten |
| 6 | Validate | Vollständige Test-Suite (unit + integration + e2e) | 103 Tests, pytest.ini, conftest-Fixtures |
| 7 | Deploy | CI/CD + Dockerfile + docker-compose | 3 Workflow-Dateien, Dockerfile, entrypoint.sh |
| 8 | Deploy | Git-Setup + .gitignore + Push-Befehle | .gitignore, 56 getrackte Cache-Dateien bereinigt, .env entfernt |
| 9 | Deploy | Commit und Push zu GitHub | Sauberes Working Tree bestätigt, zu origin/main gepusht |
| 10 | Develop | AGENTS.md mit vollständigem Session-Protokoll aktualisieren | Session-3-Dokumentation |
| 11 | Develop | Minimale Web-UI unter /ui mit 4 Tabs | index.html, StaticFiles-Mount, /ui-Route |
| 12 | Develop | Anwendungsschicht (Use-Cases) + in Router einbinden | use_cases.py, appointments- und inventory-Router aktualisiert |
| 13 | Develop | Anwendungsschicht-Docs + Use-Case-Spezifikationen hinzufügen | docs/PROJECT.md, UC-001, UC-002, docs/TASKS.md |
| 14 | Develop | KI-SDLC-Umstrukturierung: skills/-Ordner + neues AGENTS.md | skills/*.md, AGENTS.md (diese Datei), scripts/setup-skills.sh |
| 15 | Deploy | Alle aktuellen Änderungen committen und zu GitHub pushen | Sauberes Working Tree bestätigt; .env nicht getrackt bestätigt; gepusht |
| 16 | Validate | CI-Workflow schlägt bei Unit-Tests fehl — Logs prüfen und beheben | `--no-cache-dir` + `cache: "pip"`-Widerspruch identifiziert; Flag aus ci.yml entfernt |
| 17 | Validate | Terminbuchung gibt 500 zurück — debuggen und beheben | `TypeError` aus timezone-aware vs. naive datetime-Vergleich diagnostiziert; appointment.py + index.html behoben |
| 18 | Deploy | Git-Tag v1.0.0 erstellen und pushen, um Release + CD auszulösen | Tag gepusht; Release (GHCR) und CD (Render)-Pipelines ausgelöst |
| 19 | Deploy | CD-Workflow schlägt fehl — welches Secret wird erwartet? | cd.yml gelesen; benötigtes Secret identifiziert: `RENDER_DEPLOY_HOOK_URL` |
| 20 | Deploy | git tag v1.0.2 + git push origin v1.0.2 | Tag nach Render-Secret-Konfiguration gepusht |
| 21 | Develop | Mermaid-Architekturdiagramm zu docs/PROJECT.md hinzufügen | ASCII-Boxdiagramm durch farbkodierten Mermaid-`graph TD` ersetzt |
| 22 | Develop | /health-Endpunkt in README.md dokumentieren + Live-API-Badge | Vollständiges README mit CI-Badge, shields.io-Health-Badge, Endpunkt-Docs, Schnellstart |
| 23 | Develop | AGENTS.md mit letzten Session-Prompts aktualisieren | Dieser Eintrag — Prompts 15–23 hinzugefügt, Lektionen 7–8 hinzugefügt |

---

## Mensch vs. KI — Übersichtstabelle

### Menschlich verfasst (keine KI-Beteiligung)

| Artefakt | Warum menschlich |
|----------|-----------------|
| Alle sechs Domänenmodell-Klassendefinitionen | Kerngeschäftslogik; definiert das Problem |
| Feldtypen, Validierungsregeln, Geschäftsmethoden | Domänenwissen; nicht aus Anforderungen ableitbar |
| `BookingService` — Konflikterkennungsalgorithmus | Geschäftsregel: wie überlappende Termine erkannt werden |
| `InventoryService` — Lagerverwaltungsregeln | Geschäftsregel: Upsert-Semantik, Unterbestandsverhinderung |
| Abstrakte Repository-Verträge (`ABCs`) | Architekturentscheidung: was Persistenz garantieren muss |
| Clean Architecture als Strukturmuster | Bewusste Projektstrukturentscheidung |
| Datenbankzugangsdaten (`.env`) | Sicherheit |
| Entscheidung für Render als Cloud-Deployment | Infrastrukturentscheidung |
| Entscheidung für PostgreSQL als Datenbank | Infrastrukturentscheidung |

### KI-generiert (Claude Code, aus Prompt-Kontext)

| Artefakt | Wie Claude es ableitete |
|----------|------------------------|
| Alle 4 FastAPI-Router + Pydantic-Schemas | Aus Domänenmodellen und Service-Methoden-Signaturen abgeleitet |
| SQLAlchemy ORM-Modelle (alle 6 Entitäten) | Aus Domänenmodell-Feldern und Beziehungsstruktur abgeleitet |
| Alle 6 `SQLAlchemy*Repository`-Implementierungen | Aus abstrakten Repository-Verträgen abgeleitet |
| `object.__new__()`-Mapper-Muster | Erkannt, dass `__post_init__`-Guards bei DB-Hydration fehlschlagen |
| `safe_commit()`-Context-Manager | Nach Diagnose eines live `IntegrityError`-Tracebacks entworfen |
| `DuplicateEntryError`-Exception-Hierarchie | Konsequenz des `safe_commit`-Designs |
| 103 Tests über unit / integration / e2e | Aus API-Oberfläche, Domänenregeln und Edge-Cases entworfen |
| Test-Isolation via Tabellen-Truncation | Inkompatibilität von Rollback mit `db.commit()` in saves identifiziert |
| Zweistufiges Dockerfile | Best Practice auf Projektstruktur angewendet |
| `entrypoint.sh` mit Migrations-on-Start | Idiomatisches Alembic-Muster für Single-Container-Deployments |
| CI/CD-Workflow-YAML-Dateien (3) | Aus Toolchain abgeleitet (pytest, Docker, Render Deploy-Hook) |
| `.gitignore` | Standard-Python-Vorlage |
| Web-UI (HTML/CSS/JS) | Aus API-Endpunkt-Signaturen entworfen |
| `BookingUseCase` + `InventoryUseCase` | Aus Workflow im `book_appointment`-Router-Endpunkt abgeleitet |
| `docs/PROJECT.md` + Use-Case-Spezifikationen | Aus allen Projekt-Artefakten synthetisiert |
| `skills/`-Dateien (diese Umstrukturierung) | Aus vollständiger Session-Historie synthetisiert |
| CI-Fix: `--no-cache-dir` aus ci.yml entfernen | Widerspruch zwischen `cache: "pip"` und `--no-cache-dir` durch GHA-Post-Step-Fehler diagnostiziert |
| Timezone-Fix: `appointment.py` + `index.html` | 500 → `TypeError` aus aware-vs.-naive datetime-Vergleich zurückverfolgt; Zwei-Schicht-Fix vorgeschlagen |
| Mermaid-Architekturdiagramm | Aus Schichtbeschreibungen in docs/PROJECT.md generiert |
| Vollständiges README mit Badges und Endpunkt-Docs | Aus Projektstruktur, CI-Workflow-Namen und `/health`-Route abgeleitet |

---

## Architekturentscheidungen

Vollständiges Architekturdokument: [docs/PROJECT.md](docs/PROJECT.md)

Wichtigste Entscheidungen im Überblick:

| Entscheidung | Begründung |
|--------------|------------|
| Clean Architecture (4 Schichten) | Trennung der Verantwortlichkeiten; Domäne ohne DB oder HTTP testbar |
| `object.__new__()` für DB-Hydration | `__post_init__`-Guards sind Schreib-Zeit-Regeln, keine Lese-Zeit-Invarianten |
| `safe_commit()` + `DuplicateEntryError` | Einzelner Ort für `IntegrityError`-Behandlung; 409 ≠ 422 |
| `lazy="joined"` auf immer benötigten Beziehungen | Eliminiert N+1-Abfragen auf Listen-Endpunkten |
| Anwendungsschicht für Orchestrierung | ID-Auflösungslogik gehört über den HTTP-Adapter |
| Truncation (kein Rollback) für Test-Isolation | `db.commit()` in saves ist inkompatibel mit Savepoint-Rollback |
| Migrations-on-Container-Start | Idempotent, zero-downtime-sicher für Alembics inkrementelles Modell |

---

## Projektstatus

**Lebenszyklusphase: DEPLOYED** (ab 2026-05-10)

```bash
# Alle 39 Unit-Tests (keine DB erforderlich)
pytest tests/unit/ -v          # → 39 passed in 0.12s

# Vollständige Suite (erfordert medistock_test DB)
pytest                         # → 103 passed

# Lokaler Server
uvicorn medistock.interfaces.api.main:app --reload
# → http://127.0.0.1:8000/ui       (Web-UI)
# → http://127.0.0.1:8000/docs     (Swagger)

# Docker Compose (vollständiger Stack)
docker compose up --build
```

**Repository:** https://github.com/naara011100/Capstone_Projekt_MediStock  
**Branch:** `main`  
**Neuester Tag: `v1.0.2`** — löst die Release- (GHCR Docker Push) + CD- (Render Deploy) Pipelines aus.

---

## Gelernte Lektionen

Detaillierte phasenspezifische Lektionen befinden sich in den Skill-Dateien. Die wichtigsten acht:

1. **`session.merge()` ist kein unique-constraint-bewusster Upsert.** Er schlüsselt nur nach dem Primary Key.
   Immer `save()` mit einem Guard für `IntegrityError` → 409 umhüllen.

2. **`__post_init__`-Guards sind Schreib-Zeit-, keine Lese-Zeit-Invarianten.**
   `object.__new__()` verwenden, wenn Domänenobjekte aus dem Speicher rekonstruiert werden.

3. **`.gitignore` entfernt bereits committete Dateien nicht rückwirkend.**
   `git rm --cached` im Nachhinein verwenden.

4. **Commit-innerhalb-von-save ist inkompatibel mit rollback-basierter Test-Isolation.**
   Fixtures so gestalten, dass Tabellen truncated werden, nicht Transaktionen zurückgerollt.

5. **409 (Konflikt) von 422 (ungültig) auf der HTTP-Schicht unterscheiden.**
   Dies sind verschiedene Fehlermodi und sollten Verbrauchern unterschiedliche Signale geben.

6. **KI ist am nützlichsten, wenn die Domäne bereits spezifiziert ist.**
   Claude generierte korrekte Router, ORM und Tests, weil die Domänenmodelle und ABCs präzise waren. Vage Spezifikationen erzeugen vagen Code.

7. **`cache: "pip"` und `--no-cache-dir` schließen sich in GitHub Actions gegenseitig aus.**
   `actions/setup-python` speichert den pip-Download-Cache in einem Post-Step.
   `pip install --no-cache-dir` verhindert, dass pip in dieses Verzeichnis schreibt,
   lässt es leer und lässt den Post-Step fehlschlagen — auch wenn alle Tests bestehen.
   Eines von beidem verwenden, nicht beides.

8. **`datetime.utcnow()` (naive) vs. timezone-aware Datetimes wirft `TypeError`, nicht `ValueError`.**
   Das browser-seitige `toISOString()` hängt ein `Z`-Suffix an; Pydantic v2 parst dies
   als timezone-aware `datetime`. Der Vergleich mit `datetime.utcnow()` (naive) wirft
   `TypeError`, den das router-seitige `except ValueError` nicht abfängt — was zu einem
   unbehandelten HTTP 500 führt. Fix auf beiden Schichten: zu naive UTC im `__post_init__`
   des Domänenmodells normalisieren und `toISOString()` im Frontend nicht mehr aufrufen.
