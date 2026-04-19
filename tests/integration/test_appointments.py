"""
Integration tests for the appointments router.

Uses the created_patient / created_doctor / created_room / created_appointment
fixtures from tests/integration/conftest.py.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4


def _future_iso(hours: int = 48) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).isoformat()


# ---------------------------------------------------------------------------
# POST /api/v1/appointments/
# ---------------------------------------------------------------------------

def test_book_appointment_returns_201(client, appointment_payload):
    resp = client.post("/api/v1/appointments/", json=appointment_payload)
    assert resp.status_code == 201


def test_book_appointment_response_fields(client, appointment_payload, created_patient, created_doctor, created_room):
    data = client.post("/api/v1/appointments/", json=appointment_payload).json()
    assert data["status"] == "scheduled"
    assert data["patient_id"] == created_patient["id"]
    assert data["doctor_id"] == created_doctor["id"]
    assert data["room_id"] == created_room["id"]
    assert data["duration_minutes"] == 60
    assert data["notes"] == "Initial consultation"
    assert "id" in data


def test_book_appointment_past_time_returns_422(client, appointment_payload):
    appointment_payload["scheduled_at"] = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    resp = client.post("/api/v1/appointments/", json=appointment_payload)
    assert resp.status_code == 422


def test_book_appointment_unknown_patient_returns_404(client, created_doctor, created_room):
    payload = {
        "patient_id": str(uuid4()),
        "doctor_id": created_doctor["id"],
        "room_id": created_room["id"],
        "scheduled_at": _future_iso(),
        "duration_minutes": 30,
    }
    resp = client.post("/api/v1/appointments/", json=payload)
    assert resp.status_code == 404


def test_book_appointment_doctor_conflict_returns_422(client, appointment_payload, created_patient, created_doctor, created_room):
    # Book at the same time with the same doctor → conflict
    client.post("/api/v1/appointments/", json=appointment_payload)

    # Second patient, same doctor, same time
    second_patient = client.post("/api/v1/patients/", json={
        "first_name": "Bob", "last_name": "Test",
        "date_of_birth": "1985-06-01",
        "email": "bob@test.de", "phone": "9999",
    }).json()
    second_room = client.post("/api/v1/rooms/", json={"name": "Room 202", "floor": 2, "capacity": 1}).json()

    resp = client.post("/api/v1/appointments/", json={
        **appointment_payload,
        "patient_id": second_patient["id"],
        "room_id": second_room["id"],
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/appointments/
# ---------------------------------------------------------------------------

def test_list_appointments_empty(client):
    resp = client.get("/api/v1/appointments/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_appointments_returns_booked(client, created_appointment):
    data = client.get("/api/v1/appointments/").json()
    assert len(data) == 1
    assert data[0]["id"] == created_appointment["id"]


# ---------------------------------------------------------------------------
# GET /api/v1/appointments/{id}
# ---------------------------------------------------------------------------

def test_get_appointment_by_id(client, created_appointment):
    resp = client.get(f"/api/v1/appointments/{created_appointment['id']}")
    assert resp.status_code == 200


def test_get_appointment_not_found(client):
    resp = client.get(f"/api/v1/appointments/{uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH status transitions
# ---------------------------------------------------------------------------

def test_confirm_appointment(client, created_appointment):
    appt_id = created_appointment["id"]
    resp = client.patch(f"/api/v1/appointments/{appt_id}/confirm")
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


def test_complete_appointment(client, created_appointment):
    appt_id = created_appointment["id"]
    client.patch(f"/api/v1/appointments/{appt_id}/confirm")
    resp = client.patch(f"/api/v1/appointments/{appt_id}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


def test_cancel_appointment(client, created_appointment):
    appt_id = created_appointment["id"]
    resp = client.patch(f"/api/v1/appointments/{appt_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_mark_no_show(client, created_appointment):
    appt_id = created_appointment["id"]
    client.patch(f"/api/v1/appointments/{appt_id}/confirm")
    resp = client.patch(f"/api/v1/appointments/{appt_id}/no-show")
    assert resp.status_code == 200
    assert resp.json()["status"] == "no_show"


def test_complete_without_confirm_returns_422(client, created_appointment):
    appt_id = created_appointment["id"]
    resp = client.patch(f"/api/v1/appointments/{appt_id}/complete")
    assert resp.status_code == 422


def test_cancel_completed_appointment_returns_422(client, created_appointment):
    appt_id = created_appointment["id"]
    client.patch(f"/api/v1/appointments/{appt_id}/confirm")
    client.patch(f"/api/v1/appointments/{appt_id}/complete")
    resp = client.patch(f"/api/v1/appointments/{appt_id}/cancel")
    assert resp.status_code == 422
