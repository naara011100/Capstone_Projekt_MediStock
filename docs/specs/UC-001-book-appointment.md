# UC-001 — Termin buchen

| Feld | Wert |
|------|------|
| **ID** | UC-001 |
| **Name** | Termin buchen |
| **Version** | 1.0 |
| **Status** | Implementiert |
| **Schicht** | `BookingUseCase.book()` → `BookingService.book_appointment()` |
| **API-Endpunkt** | `POST /api/v1/appointments/` |

---

## Akteure

| Akteur | Rolle |
|--------|-------|
| Krankenhauspersonal (Rezeptionist) | Startet die Buchung über die Web-Oberfläche oder REST API |
| MediStock-System | Prüft Verfügbarkeit, erkennt Konflikte, speichert den Termin |

---

## Vorbedingungen

1. Der **Patient** mit `patient_id` existiert und ist aktiv.
2. Der **Arzt** mit `doctor_id` existiert und ist aktiv.
3. Der **Raum** mit `room_id` existiert.
4. Der gewünschte `scheduled_at`-Zeitstempel liegt in der Zukunft (UTC).
5. `duration_minutes` ist eine positive ganze Zahl.

---

## Hauptablauf (Happy Path)

```
Personal → API: POST /api/v1/appointments/
                { patient_id, doctor_id, room_id,
                  scheduled_at, duration_minutes, notes }

1. BookingUseCase.book() löst patient_id → Patient-Domänenobjekt auf.
   └─ Falls nicht gefunden → LookupError("Patient not found.") → HTTP 404

2. BookingUseCase.book() löst doctor_id → Doctor-Domänenobjekt auf.
   └─ Falls nicht gefunden → LookupError("Doctor not found.") → HTTP 404

3. BookingUseCase.book() löst room_id → Room-Domänenobjekt auf.
   └─ Falls nicht gefunden → LookupError("Room not found.") → HTTP 404

4. BookingService.book_appointment() erstellt ein Appointment-Domänenobjekt.
   Domänenvalidierung (Appointment.__post_init__):
   └─ scheduled_at muss > utcnow() sein  → ValueError → HTTP 422
   └─ duration_minutes muss > 0 sein     → ValueError → HTTP 422

5. BookingService._check_conflicts() prüft alle SCHEDULED- und CONFIRMED-
   Termine auf Zeitüberschneidungen (basierend auf Start + Dauer):
   └─ Arzt bereits gebucht      → ValueError → HTTP 422
   └─ Patient bereits gebucht   → ValueError → HTTP 422
   └─ Raum bereits gebucht      → ValueError → HTTP 422

6. AppointmentRepository.save() speichert den neuen Termin (status = SCHEDULED).

7. API gibt HTTP 201 mit AppointmentResponse zurück.
```

---

## Alternativabläufe

### A1 — Patient nicht gefunden
- Schritt 1 schlägt fehl, da kein Patient mit der angegebenen UUID existiert.
- Antwort: `HTTP 404 { "detail": "Patient not found." }`

### A2 — Arzt nicht gefunden
- Schritt 2 schlägt fehl.
- Antwort: `HTTP 404 { "detail": "Doctor not found." }`

### A3 — Raum nicht gefunden
- Schritt 3 schlägt fehl.
- Antwort: `HTTP 404 { "detail": "Room not found." }`

### A4 — Termin in der Vergangenheit
- Schritt 4 schlägt bei der Domänenvalidierung fehl: `scheduled_at <= utcnow()`.
- Antwort: `HTTP 422 { "detail": "Appointment must be scheduled in the future." }`

### A5 — Arzt hat einen Konflikttermin
- Schritt 5 erkennt, dass der Arzt bereits einen SCHEDULED- oder CONFIRMED-Termin hat,
  dessen Zeitfenster mit dem gewünschten Slot überlappt.
- Antwort: `HTTP 422 { "detail": "Doctor '...' already has an appointment at ..." }`

### A6 — Patient hat einen Konflikttermin
- Wie A5, aber für den Patienten.
- Antwort: `HTTP 422 { "detail": "Patient '...' already has an appointment at ..." }`

### A7 — Raum bereits gebucht
- Wie A5, aber für den Raum.
- Antwort: `HTTP 422 { "detail": "Room '...' is already booked at ..." }`

---

## Nachbedingungen

- Ein neuer `Appointment`-Datensatz existiert in der Datenbank mit `status = SCHEDULED`.
- Die Termin-ID wird im Antwort-Body zurückgegeben.

---

## Geschäftsregeln

| Regel | Wo durchgesetzt |
|-------|----------------|
| `scheduled_at` muss in der Zukunft liegen | `Appointment.__post_init__` |
| `duration_minutes` muss > 0 sein | `Appointment.__post_init__` |
| Zwei aktive Termine dürfen sich für denselben Arzt nicht überschneiden | `BookingService._check_conflicts()` |
| Zwei aktive Termine dürfen sich für denselben Patienten nicht überschneiden | `BookingService._check_conflicts()` |
| Zwei aktive Termine dürfen denselben Raum nicht gleichzeitig belegen | `BookingService._check_conflicts()` |
| Nur SCHEDULED- / CONFIRMED-Termine werden auf Konflikte geprüft | `BookingService._check_conflicts()` |

---

## Termin-Status-Zustandsmaschine

```
           book()
             │
             ▼
         SCHEDULED
         /        \
   confirm()    cancel()
       │              │
       ▼              ▼
   CONFIRMED      CANCELLED
   /   |    \
complete() cancel() mark_no_show()
   │              │
   ▼              ▼
COMPLETED      NO_SHOW
```

---

## Verwandte Use-Cases

- UC-002 — Medikamentenbestand verwalten (paralleler Workflow, keine Abhängigkeit)
