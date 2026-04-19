"""
Integration-test fixtures for pre-created domain entities.

These fixtures use the shared `client` from tests/conftest.py to POST
entities into the test database so individual test functions can focus
on the specific behavior they are verifying.
"""
import pytest
from datetime import datetime, timedelta


PATIENT_PAYLOAD = {
    "first_name": "Anna",
    "last_name": "Mueller",
    "date_of_birth": "1990-05-15",
    "email": "anna@test.de",
    "phone": "0123456789",
}

DOCTOR_PAYLOAD = {
    "first_name": "Max",
    "last_name": "Schmidt",
    "specialization": "Cardiology",
    "email": "max@hospital.de",
    "phone": "0456789123",
}

ROOM_PAYLOAD = {"name": "Room 101", "floor": 1, "capacity": 2}

MEDICATION_PAYLOAD = {
    "name": "Aspirin",
    "description": "Pain reliever",
    "unit": "tablet",
}


def _future_iso(hours: int = 48) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).isoformat()


@pytest.fixture
def created_patient(client):
    return client.post("/api/v1/patients/", json=PATIENT_PAYLOAD).json()


@pytest.fixture
def created_doctor(client):
    return client.post("/api/v1/doctors/", json=DOCTOR_PAYLOAD).json()


@pytest.fixture
def created_room(client):
    return client.post("/api/v1/rooms/", json=ROOM_PAYLOAD).json()


@pytest.fixture
def created_medication(client):
    return client.post("/api/v1/inventory/medications", json=MEDICATION_PAYLOAD).json()


@pytest.fixture
def appointment_payload(created_patient, created_doctor, created_room):
    return {
        "patient_id": created_patient["id"],
        "doctor_id": created_doctor["id"],
        "room_id": created_room["id"],
        "scheduled_at": _future_iso(48),
        "duration_minutes": 60,
        "notes": "Initial consultation",
    }


@pytest.fixture
def created_appointment(client, appointment_payload):
    return client.post("/api/v1/appointments/", json=appointment_payload).json()
