"""
End-to-end workflow tests.

Each test exercises a complete user journey through the HTTP API, verifying
that all layers (routing, service, repository, database) work together.
"""
import pytest
from datetime import datetime, timedelta


def _future_iso(hours: int = 48) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).isoformat()


# ===========================================================================
# Workflow 1: Create entities → book appointment → confirm → complete
# ===========================================================================

def test_full_appointment_lifecycle(client):
    # 1. Create a doctor
    doctor = client.post("/api/v1/doctors/", json={
        "first_name": "Eva", "last_name": "Klein",
        "specialization": "Neurology",
        "email": "eva@hospital.de", "phone": "0111",
    }).json()
    assert "id" in doctor

    # 2. Create a patient
    patient = client.post("/api/v1/patients/", json={
        "first_name": "Leon", "last_name": "Braun",
        "date_of_birth": "1985-03-20",
        "email": "leon@test.de", "phone": "0222",
    }).json()
    assert "id" in patient

    # 3. Create a room
    room = client.post("/api/v1/rooms/", json={
        "name": "Neurology Suite", "floor": 3, "capacity": 1,
    }).json()
    assert room["is_available"] is True

    # 4. Book appointment
    appt = client.post("/api/v1/appointments/", json={
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "room_id": room["id"],
        "scheduled_at": _future_iso(24),
        "duration_minutes": 45,
        "notes": "First visit",
    }).json()
    assert appt["status"] == "scheduled"

    # 5. Confirm
    confirmed = client.patch(f"/api/v1/appointments/{appt['id']}/confirm").json()
    assert confirmed["status"] == "confirmed"

    # 6. Complete
    completed = client.patch(f"/api/v1/appointments/{appt['id']}/complete").json()
    assert completed["status"] == "completed"

    # 7. Verify appointment appears in list
    all_appts = client.get("/api/v1/appointments/").json()
    assert any(a["id"] == appt["id"] for a in all_appts)


def test_appointment_cancel_workflow(client):
    doctor = client.post("/api/v1/doctors/", json={
        "first_name": "Tom", "last_name": "Wolf",
        "specialization": "General", "email": "tom@hospital.de", "phone": "0333",
    }).json()
    patient = client.post("/api/v1/patients/", json={
        "first_name": "Mia", "last_name": "Fischer",
        "date_of_birth": "1992-07-10",
        "email": "mia@test.de", "phone": "0444",
    }).json()
    room = client.post("/api/v1/rooms/", json={"name": "General Ward", "floor": 1, "capacity": 3}).json()

    appt = client.post("/api/v1/appointments/", json={
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "room_id": room["id"],
        "scheduled_at": _future_iso(12),
        "duration_minutes": 30,
    }).json()

    # Cancel directly from SCHEDULED
    cancelled = client.patch(f"/api/v1/appointments/{appt['id']}/cancel").json()
    assert cancelled["status"] == "cancelled"

    # Cannot cancel again
    resp = client.patch(f"/api/v1/appointments/{appt['id']}/cancel")
    assert resp.status_code == 422


def test_appointment_no_show_workflow(client):
    doctor = client.post("/api/v1/doctors/", json={
        "first_name": "Sara", "last_name": "Bauer",
        "specialization": "Pediatrics", "email": "sara@hospital.de", "phone": "0555",
    }).json()
    patient = client.post("/api/v1/patients/", json={
        "first_name": "Erik", "last_name": "Schulz",
        "date_of_birth": "2000-01-15",
        "email": "erik@test.de", "phone": "0666",
    }).json()
    room = client.post("/api/v1/rooms/", json={"name": "Pediatrics A", "floor": 2, "capacity": 2}).json()

    appt = client.post("/api/v1/appointments/", json={
        "patient_id": patient["id"],
        "doctor_id": doctor["id"],
        "room_id": room["id"],
        "scheduled_at": _future_iso(8),
        "duration_minutes": 20,
    }).json()

    client.patch(f"/api/v1/appointments/{appt['id']}/confirm")
    no_show = client.patch(f"/api/v1/appointments/{appt['id']}/no-show").json()
    assert no_show["status"] == "no_show"


# ===========================================================================
# Workflow 2: Create medication → add stock → dispense → low-stock alert
# ===========================================================================

def test_full_inventory_lifecycle(client):
    # 1. Create medication
    med = client.post("/api/v1/inventory/medications", json={
        "name": "Paracetamol", "description": "Fever reducer", "unit": "tablet",
    }).json()
    assert med["is_active"] is True

    # 2. No stock yet — list should be empty
    assert client.get("/api/v1/inventory/stock").json() == []

    # 3. Add initial stock (100 tablets)
    stock = client.post("/api/v1/inventory/stock/add", json={
        "medication_id": med["id"], "amount": 100, "location": "Cabinet B",
    }).json()
    assert stock["quantity"] == 100
    assert stock["is_low"] is False
    assert stock["is_out_of_stock"] is False

    # 4. No low-stock alert yet
    assert client.get("/api/v1/inventory/stock/low-stock").json() == []

    # 5. Dispense 92 tablets → 8 remaining (below threshold of 10)
    stock = client.post("/api/v1/inventory/stock/dispense", json={
        "medication_id": med["id"], "amount": 92,
    }).json()
    assert stock["quantity"] == 8
    assert stock["is_low"] is True

    # 6. Low-stock alert appears
    alerts = client.get("/api/v1/inventory/stock/low-stock").json()
    assert len(alerts) == 1
    assert alerts[0]["medication_name"] == "Paracetamol"

    # 7. Restock (add 50 more)
    stock = client.post("/api/v1/inventory/stock/add", json={
        "medication_id": med["id"], "amount": 50, "location": "Cabinet B",
    }).json()
    assert stock["quantity"] == 58
    assert stock["is_low"] is False

    # 8. Alert gone
    assert client.get("/api/v1/inventory/stock/low-stock").json() == []


def test_dispense_entire_stock_triggers_out_of_stock(client):
    med = client.post("/api/v1/inventory/medications", json={
        "name": "Morphine", "description": "Analgesic", "unit": "mg",
    }).json()

    client.post("/api/v1/inventory/stock/add", json={
        "medication_id": med["id"], "amount": 5, "location": "Safe",
    })

    stock = client.post("/api/v1/inventory/stock/dispense", json={
        "medication_id": med["id"], "amount": 5,
    }).json()
    assert stock["is_out_of_stock"] is True
    assert stock["quantity"] == 0


def test_dispense_more_than_available_returns_422(client):
    med = client.post("/api/v1/inventory/medications", json={
        "name": "Insulin", "description": "Hormone", "unit": "unit",
    }).json()

    client.post("/api/v1/inventory/stock/add", json={
        "medication_id": med["id"], "amount": 3, "location": "Fridge",
    })

    resp = client.post("/api/v1/inventory/stock/dispense", json={
        "medication_id": med["id"], "amount": 10,
    })
    assert resp.status_code == 422


# ===========================================================================
# Workflow 3: Doctor deactivation does not block existing data
# ===========================================================================

def test_deactivate_doctor_still_visible_in_list(client):
    doctor = client.post("/api/v1/doctors/", json={
        "first_name": "Old", "last_name": "Doc",
        "specialization": "Retired", "email": "old@hospital.de", "phone": "0000",
    }).json()

    client.delete(f"/api/v1/doctors/{doctor['id']}")

    # Doctor record persists (soft delete)
    data = client.get("/api/v1/doctors/").json()
    match = next((d for d in data if d["id"] == doctor["id"]), None)
    assert match is not None
    assert match["is_active"] is False
