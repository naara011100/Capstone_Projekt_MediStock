"""
Integration tests for the inventory router (medications + stock).
"""
from uuid import uuid4


MEDICATION = {"name": "Ibuprofen", "description": "Anti-inflammatory", "unit": "tablet"}


# ---------------------------------------------------------------------------
# Medications
# ---------------------------------------------------------------------------

def test_create_medication_returns_201(client):
    resp = client.post("/api/v1/inventory/medications", json=MEDICATION)
    assert resp.status_code == 201


def test_create_medication_response_fields(client):
    data = client.post("/api/v1/inventory/medications", json=MEDICATION).json()
    assert data["name"] == "Ibuprofen"
    assert data["unit"] == "tablet"
    assert data["is_active"] is True


def test_create_medication_duplicate_name_returns_409(client):
    client.post("/api/v1/inventory/medications", json=MEDICATION)
    resp = client.post("/api/v1/inventory/medications", json=MEDICATION)
    assert resp.status_code == 409


def test_create_medication_empty_name_returns_422(client):
    resp = client.post("/api/v1/inventory/medications", json={**MEDICATION, "name": "  "})
    assert resp.status_code == 422


def test_list_medications_empty(client):
    assert client.get("/api/v1/inventory/medications").json() == []


def test_list_medications_returns_created(client):
    client.post("/api/v1/inventory/medications", json=MEDICATION)
    data = client.get("/api/v1/inventory/medications").json()
    assert len(data) == 1


def test_get_medication_by_id(client):
    created = client.post("/api/v1/inventory/medications", json=MEDICATION).json()
    resp = client.get(f"/api/v1/inventory/medications/{created['id']}")
    assert resp.status_code == 200


def test_get_medication_not_found(client):
    resp = client.get(f"/api/v1/inventory/medications/{uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Stock — add
# ---------------------------------------------------------------------------

def test_add_stock_returns_200(client, created_medication):
    resp = client.post("/api/v1/inventory/stock/add", json={
        "medication_id": created_medication["id"],
        "amount": 100,
        "location": "Shelf A",
    })
    assert resp.status_code == 200


def test_add_stock_response_fields(client, created_medication):
    data = client.post("/api/v1/inventory/stock/add", json={
        "medication_id": created_medication["id"],
        "amount": 50,
        "location": "Shelf B",
    }).json()
    assert data["quantity"] == 50
    assert data["location"] == "Shelf B"
    assert data["is_out_of_stock"] is False


def test_add_stock_accumulates(client, created_medication):
    med_id = created_medication["id"]
    client.post("/api/v1/inventory/stock/add", json={"medication_id": med_id, "amount": 30, "location": "X"})
    data = client.post("/api/v1/inventory/stock/add", json={"medication_id": med_id, "amount": 20, "location": "X"}).json()
    assert data["quantity"] == 50


def test_add_stock_unknown_medication_returns_404(client):
    resp = client.post("/api/v1/inventory/stock/add", json={
        "medication_id": str(uuid4()), "amount": 10, "location": "X"
    })
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Stock — dispense
# ---------------------------------------------------------------------------

def test_dispense_stock_reduces_quantity(client, created_medication):
    med_id = created_medication["id"]
    client.post("/api/v1/inventory/stock/add", json={"medication_id": med_id, "amount": 100, "location": "X"})
    data = client.post("/api/v1/inventory/stock/dispense", json={"medication_id": med_id, "amount": 30}).json()
    assert data["quantity"] == 70


def test_dispense_insufficient_stock_returns_422(client, created_medication):
    med_id = created_medication["id"]
    client.post("/api/v1/inventory/stock/add", json={"medication_id": med_id, "amount": 5, "location": "X"})
    resp = client.post("/api/v1/inventory/stock/dispense", json={"medication_id": med_id, "amount": 10})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Stock — low stock alert
# ---------------------------------------------------------------------------

def test_low_stock_alert_triggered(client, created_medication):
    med_id = created_medication["id"]
    # Add only 5 units — below the default threshold of 10
    client.post("/api/v1/inventory/stock/add", json={"medication_id": med_id, "amount": 5, "location": "X"})

    data = client.get("/api/v1/inventory/stock/low-stock").json()
    assert len(data) == 1
    assert data[0]["is_low"] is True


def test_no_low_stock_alert_when_above_threshold(client, created_medication):
    med_id = created_medication["id"]
    client.post("/api/v1/inventory/stock/add", json={"medication_id": med_id, "amount": 100, "location": "X"})

    data = client.get("/api/v1/inventory/stock/low-stock").json()
    assert data == []
