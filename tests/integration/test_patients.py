import pytest
from uuid import uuid4


VALID = {
    "first_name": "Anna",
    "last_name": "Mueller",
    "date_of_birth": "1990-05-15",
    "email": "anna@test.de",
    "phone": "0123456789",
}


# ---------------------------------------------------------------------------
# POST /api/v1/patients/
# ---------------------------------------------------------------------------

def test_create_patient_returns_201(client):
    resp = client.post("/api/v1/patients/", json=VALID)
    assert resp.status_code == 201


def test_create_patient_response_fields(client):
    data = client.post("/api/v1/patients/", json=VALID).json()
    assert data["first_name"] == "Anna"
    assert data["last_name"] == "Mueller"
    assert data["email"] == "anna@test.de"
    assert data["full_name"] == "Anna Mueller"
    assert data["is_active"] is True
    assert "id" in data


def test_create_patient_duplicate_email_returns_409(client):
    client.post("/api/v1/patients/", json=VALID)
    resp = client.post("/api/v1/patients/", json=VALID)
    assert resp.status_code == 409


def test_create_patient_invalid_email_returns_422(client):
    resp = client.post("/api/v1/patients/", json={**VALID, "email": "not-an-email"})
    assert resp.status_code == 422


def test_create_patient_future_dob_returns_422(client):
    resp = client.post("/api/v1/patients/", json={**VALID, "date_of_birth": "2099-01-01"})
    assert resp.status_code == 422


def test_create_patient_empty_first_name_returns_422(client):
    resp = client.post("/api/v1/patients/", json={**VALID, "first_name": "   "})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/patients/
# ---------------------------------------------------------------------------

def test_list_patients_empty(client):
    resp = client.get("/api/v1/patients/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_patients_returns_created(client):
    client.post("/api/v1/patients/", json=VALID)
    data = client.get("/api/v1/patients/").json()
    assert len(data) == 1
    assert data[0]["email"] == "anna@test.de"


# ---------------------------------------------------------------------------
# GET /api/v1/patients/{id}
# ---------------------------------------------------------------------------

def test_get_patient_by_id(client):
    created = client.post("/api/v1/patients/", json=VALID).json()
    resp = client.get(f"/api/v1/patients/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_patient_not_found_returns_404(client):
    resp = client.get(f"/api/v1/patients/{uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/patients/{id}  (deactivate)
# ---------------------------------------------------------------------------

def test_deactivate_patient_returns_204(client):
    created = client.post("/api/v1/patients/", json=VALID).json()
    resp = client.delete(f"/api/v1/patients/{created['id']}")
    assert resp.status_code == 204


def test_deactivate_nonexistent_patient_returns_404(client):
    resp = client.delete(f"/api/v1/patients/{uuid4()}")
    assert resp.status_code == 404
