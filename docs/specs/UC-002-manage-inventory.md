# UC-002 — Manage Medication Inventory

| Field | Value |
|-------|-------|
| **ID** | UC-002 |
| **Name** | Manage Medication Inventory |
| **Version** | 1.0 |
| **Status** | Implemented |
| **Layer** | `InventoryUseCase` → `InventoryService` |
| **API endpoints** | `POST /api/v1/inventory/stock/add`, `POST /api/v1/inventory/stock/dispense` |

---

## Actors

| Actor | Role |
|-------|------|
| Pharmacist / Hospital Staff | Adds deliveries, dispenses medication |
| MediStock System | Tracks quantities, raises low-stock alerts |

---

## Preconditions

- A **Medication** record identified by `medication_id` exists in the database.
- For dispensing: a `StockItem` record exists for that medication.

---

## Use Case 1 — Add Stock

### Main Flow

```
Staff → API: POST /api/v1/inventory/stock/add
             { medication_id, amount, location }

1. InventoryUseCase.add_stock() resolves medication_id → Medication domain object.
   └─ If not found → LookupError("Medication not found.") → HTTP 404

2. InventoryService.add_stock() checks for an existing StockItem for this medication.
   └─ If none exists → creates a new StockItem(quantity=0, location=location)

3. StockItem.add_stock(amount) increases the quantity.
   └─ amount must be > 0 → ValueError → HTTP 422

4. StockRepository.save() persists the StockItem.

5. API returns HTTP 200 with StockItemResponse (includes is_low, is_out_of_stock flags).
```

### Business Rules

| Rule | Where enforced |
|------|----------------|
| `amount` must be positive | `StockItem.add_stock()` |
| One stock entry per medication (upsert semantics) | `InventoryService.add_stock()` |

---

## Use Case 2 — Dispense Stock

### Main Flow

```
Staff → API: POST /api/v1/inventory/stock/dispense
             { medication_id, amount }

1. InventoryUseCase.dispense() resolves medication_id → Medication domain object.
   └─ If not found → LookupError("Medication not found.") → HTTP 404

2. InventoryService.dispense() retrieves the StockItem.
   └─ If no stock entry → ValueError("No stock entry found…") → HTTP 422

3. StockItem.dispense(amount) reduces the quantity.
   └─ amount must be > 0             → ValueError → HTTP 422
   └─ quantity must not go negative  → ValueError → HTTP 422

4. StockRepository.save() persists the updated StockItem.

5. API returns HTTP 200 with StockItemResponse.
```

### Business Rules

| Rule | Where enforced |
|------|----------------|
| `amount` must be positive | `StockItem.dispense()` |
| Quantity cannot go below zero (no negative stock) | `StockItem.dispense()` |
| A stock entry must already exist before dispensing | `InventoryService.dispense()` |

---

## Use Case 3 — View Stock and Low-Stock Alerts

### Main Flow

```
Staff → API: GET /api/v1/inventory/stock
             → list of all StockItemResponse objects

Staff → API: GET /api/v1/inventory/stock/low-stock
             → filtered list where quantity ≤ low_stock_threshold (default: 10)
```

### Business Rules

| Rule | Where enforced |
|------|----------------|
| `is_low` flag = quantity ≤ `StockItem.LOW_STOCK_THRESHOLD` (10) | `StockItem.is_low` property |
| `is_out_of_stock` flag = quantity ≤ 0 | `StockItem.is_out_of_stock` property |
| Low-stock query uses a DB-level filter for performance | `SQLAlchemyStockRepository.list_low_stock()` |

---

## Alternative Flows

### A1 — Medication does not exist
- Steps 1 of add or dispense fail.
- Response: `HTTP 404 { "detail": "Medication not found." }`

### A2 — Dispense more than available
- Step 3 of dispense: `quantity - amount < 0`.
- Response: `HTTP 422 { "detail": "Insufficient stock..." }`

### A3 — No stock entry for medication
- Step 2 of dispense: `StockRepository.get_by_medication()` returns `None`.
- Response: `HTTP 422 { "detail": "No stock entry found for medication '...'." }`

---

## Post-conditions

- **Add**: `StockItem.quantity` increased by `amount`; row created if first delivery.
- **Dispense**: `StockItem.quantity` decreased by `amount`; never goes below zero.

---

## Related Use Cases

- UC-001 — Book Appointment (no dependency; concurrent workflows)
