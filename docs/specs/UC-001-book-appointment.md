# UC-001 — Book Appointment

| Field | Value |
|-------|-------|
| **ID** | UC-001 |
| **Name** | Book Appointment |
| **Version** | 1.0 |
| **Status** | Implemented |
| **Layer** | `BookingUseCase.book()` → `BookingService.book_appointment()` |
| **API endpoint** | `POST /api/v1/appointments/` |

---

## Actors

| Actor | Role |
|-------|------|
| Hospital Staff (Receptionist) | Initiates booking via the web UI or REST API |
| MediStock System | Validates availability, detects conflicts, persists appointment |

---

## Preconditions

1. The **patient** identified by `patient_id` exists and is active.
2. The **doctor** identified by `doctor_id` exists and is active.
3. The **room** identified by `room_id` exists.
4. The requested `scheduled_at` timestamp is in the future (UTC).
5. `duration_minutes` is a positive integer.

---

## Main Flow (Happy Path)

```
Staff → API: POST /api/v1/appointments/
             { patient_id, doctor_id, room_id,
               scheduled_at, duration_minutes, notes }

1. BookingUseCase.book() resolves patient_id → Patient domain object.
   └─ If not found → LookupError("Patient not found.") → HTTP 404

2. BookingUseCase.book() resolves doctor_id → Doctor domain object.
   └─ If not found → LookupError("Doctor not found.") → HTTP 404

3. BookingUseCase.book() resolves room_id → Room domain object.
   └─ If not found → LookupError("Room not found.") → HTTP 404

4. BookingService.book_appointment() constructs an Appointment domain object.
   Domain validation (Appointment.__post_init__):
   └─ scheduled_at must be > utcnow()  → ValueError → HTTP 422
   └─ duration_minutes must be > 0     → ValueError → HTTP 422

5. BookingService._check_conflicts() scans all SCHEDULED and CONFIRMED
   appointments for time overlaps (based on start + duration):
   └─ Same doctor already booked      → ValueError → HTTP 422
   └─ Same patient already booked     → ValueError → HTTP 422
   └─ Same room already booked        → ValueError → HTTP 422

6. AppointmentRepository.save() persists the new appointment (status = SCHEDULED).

7. API returns HTTP 201 with AppointmentResponse.
```

---

## Alternative Flows

### A1 — Patient not found
- Step 1 fails because no patient with the given UUID exists.
- Response: `HTTP 404 { "detail": "Patient not found." }`

### A2 — Doctor not found
- Step 2 fails.
- Response: `HTTP 404 { "detail": "Doctor not found." }`

### A3 — Room not found
- Step 3 fails.
- Response: `HTTP 404 { "detail": "Room not found." }`

### A4 — Appointment in the past
- Step 4 fails domain validation: `scheduled_at <= utcnow()`.
- Response: `HTTP 422 { "detail": "Appointment must be scheduled in the future." }`

### A5 — Doctor has a conflicting appointment
- Step 5 detects that the doctor has a SCHEDULED or CONFIRMED appointment
  whose time window overlaps with the requested slot.
- Response: `HTTP 422 { "detail": "Doctor '...' already has an appointment at ..." }`

### A6 — Patient has a conflicting appointment
- Same as A5 but for the patient.
- Response: `HTTP 422 { "detail": "Patient '...' already has an appointment at ..." }`

### A7 — Room is already booked
- Same as A5 but for the room.
- Response: `HTTP 422 { "detail": "Room '...' is already booked at ..." }`

---

## Post-conditions

- A new `Appointment` record exists in the database with `status = SCHEDULED`.
- The appointment ID is returned in the response body.

---

## Business Rules

| Rule | Where enforced |
|------|----------------|
| `scheduled_at` must be in the future | `Appointment.__post_init__` |
| `duration_minutes` must be > 0 | `Appointment.__post_init__` |
| No two active appointments may overlap for the same doctor | `BookingService._check_conflicts()` |
| No two active appointments may overlap for the same patient | `BookingService._check_conflicts()` |
| No two active appointments may occupy the same room at the same time | `BookingService._check_conflicts()` |
| Only SCHEDULED / CONFIRMED appointments are checked for conflicts | `BookingService._check_conflicts()` |

---

## Appointment Status State Machine

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

## Related Use Cases

- UC-002 — Manage Medication Inventory (parallel workflow, no dependency)
