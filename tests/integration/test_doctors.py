from uuid import uuid4


VALID = {
    "first_name": "Max",
    "last_name": "Schmidt",
    "specialization": "Cardiology",
    "email": "max@hospital.de",
    "phone": "0456789123",
}


# ---------------------------------------------------------------------------
# POST /api/v1/doctors/
# ---------------------------------------------------------------------------

def test_create_doctor_returns_201(client):
    resp = client.post("/api/v1/doctors/", json=VALID)
    assert resp.status_code == 201


def test_create_doctor_response_has_full_name(client):
    data = client.post("/api/v1/doctors/", json=VALID).json()
    assert data["full_name"] == "Dr. Max Schmidt"
    assert data["specialization"] == "Cardiology"
    assert data["is_active"] is True


def test_create_doctor_duplicate_email_returns_409(client):
    client.post("/api/v1/doctors/", json=VALID)
    resp = client.post("/api/v1/doctors/", json=VALID)
    assert resp.status_code == 409


def test_create_doctor_invalid_email_returns_422(client):
    resp = client.post("/api/v1/doctors/", json={**VALID, "email": "bad"})
    assert resp.status_code == 422


def test_create_doctor_empty_specialization_returns_422(client):
    resp = client.post("/api/v1/doctors/", json={**VALID, "specialization": "  "})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/doctors/
# ---------------------------------------------------------------------------

def test_list_doctors_empty(client):
    assert client.get("/api/v1/doctors/").json() == []


def test_list_doctors_returns_all(client):
    client.post("/api/v1/doctors/", json=VALID)
    data = client.get("/api/v1/doctors/").json()
    assert len(data) == 1


# ---------------------------------------------------------------------------
# GET /api/v1/doctors/{id}
# ---------------------------------------------------------------------------

def test_get_doctor_by_id(client):
    created = client.post("/api/v1/doctors/", json=VALID).json()
    resp = client.get(f"/api/v1/doctors/{created['id']}")
    assert resp.status_code == 200


def test_get_doctor_not_found_returns_404(client):
    resp = client.get(f"/api/v1/doctors/{uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/doctors/{id}  (deactivate)
# ---------------------------------------------------------------------------

def test_deactivate_doctor_returns_204(client):
    created = client.post("/api/v1/doctors/", json=VALID).json()
    resp = client.delete(f"/api/v1/doctors/{created['id']}")
    assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Rooms (co-located because they share the same router module)
# ---------------------------------------------------------------------------

VALID_ROOM = {"name": "Room 101", "floor": 1, "capacity": 4}


def test_create_room_returns_201(client):
    resp = client.post("/api/v1/rooms/", json=VALID_ROOM)
    assert resp.status_code == 201


def test_create_room_duplicate_name_returns_409(client):
    client.post("/api/v1/rooms/", json=VALID_ROOM)
    resp = client.post("/api/v1/rooms/", json=VALID_ROOM)
    assert resp.status_code == 409


def test_create_room_zero_capacity_returns_422(client):
    resp = client.post("/api/v1/rooms/", json={**VALID_ROOM, "capacity": 0})
    assert resp.status_code == 422


def test_room_availability_toggle(client):
    room = client.post("/api/v1/rooms/", json=VALID_ROOM).json()
    rid = room["id"]

    resp = client.patch(f"/api/v1/rooms/{rid}/unavailable")
    assert resp.status_code == 200
    assert resp.json()["is_available"] is False

    resp = client.patch(f"/api/v1/rooms/{rid}/available")
    assert resp.status_code == 200
    assert resp.json()["is_available"] is True
