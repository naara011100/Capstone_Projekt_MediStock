# UC-002 — Medikamentenbestand verwalten

| Feld | Wert |
|------|------|
| **ID** | UC-002 |
| **Name** | Medikamentenbestand verwalten |
| **Version** | 1.0 |
| **Status** | Implementiert |
| **Schicht** | `InventoryUseCase` → `InventoryService` |
| **API-Endpunkte** | `POST /api/v1/inventory/stock/add`, `POST /api/v1/inventory/stock/dispense` |

---

## Akteure

| Akteur | Rolle |
|--------|-------|
| Apotheker / Krankenhauspersonal | Nimmt Lieferungen entgegen, gibt Medikamente aus |
| MediStock-System | Verfolgt Mengen, löst Niedrigbestand-Warnungen aus |

---

## Vorbedingungen

- Ein **Medikament**-Datensatz mit `medication_id` existiert in der Datenbank.
- Für die Ausgabe: Ein `StockItem`-Datensatz für dieses Medikament existiert.

---

## Use-Case 1 — Bestand hinzufügen

### Hauptablauf

```
Personal → API: POST /api/v1/inventory/stock/add
                { medication_id, amount, location }

1. InventoryUseCase.add_stock() löst medication_id → Medication-Domänenobjekt auf.
   └─ Falls nicht gefunden → LookupError("Medication not found.") → HTTP 404

2. InventoryService.add_stock() prüft auf einen vorhandenen StockItem-Eintrag.
   └─ Falls keiner existiert → erstellt neuen StockItem(quantity=0, location=location)

3. StockItem.add_stock(amount) erhöht die Menge.
   └─ amount muss > 0 sein → ValueError → HTTP 422

4. StockRepository.save() speichert den StockItem.

5. API gibt HTTP 200 mit StockItemResponse zurück (inkl. is_low, is_out_of_stock-Flags).
```

### Geschäftsregeln

| Regel | Wo durchgesetzt |
|-------|----------------|
| `amount` muss positiv sein | `StockItem.add_stock()` |
| Ein Lagereintrag pro Medikament (Upsert-Semantik) | `InventoryService.add_stock()` |

---

## Use-Case 2 — Bestand ausgeben

### Hauptablauf

```
Personal → API: POST /api/v1/inventory/stock/dispense
                { medication_id, amount }

1. InventoryUseCase.dispense() löst medication_id → Medication-Domänenobjekt auf.
   └─ Falls nicht gefunden → LookupError("Medication not found.") → HTTP 404

2. InventoryService.dispense() ruft den StockItem ab.
   └─ Falls kein Eintrag vorhanden → ValueError("No stock entry found…") → HTTP 422

3. StockItem.dispense(amount) reduziert die Menge.
   └─ amount muss > 0 sein             → ValueError → HTTP 422
   └─ Menge darf nicht negativ werden  → ValueError → HTTP 422

4. StockRepository.save() speichert den aktualisierten StockItem.

5. API gibt HTTP 200 mit StockItemResponse zurück.
```

### Geschäftsregeln

| Regel | Wo durchgesetzt |
|-------|----------------|
| `amount` muss positiv sein | `StockItem.dispense()` |
| Menge darf nicht unter null sinken (kein negativer Bestand) | `StockItem.dispense()` |
| Ein Lagereintrag muss vor der Ausgabe existieren | `InventoryService.dispense()` |

---

## Use-Case 3 — Bestand und Niedrigbestand-Warnungen anzeigen

### Hauptablauf

```
Personal → API: GET /api/v1/inventory/stock
                → Liste aller StockItemResponse-Objekte

Personal → API: GET /api/v1/inventory/stock/low-stock
                → gefilterte Liste mit quantity ≤ low_stock_threshold (Standard: 10)
```

### Geschäftsregeln

| Regel | Wo durchgesetzt |
|-------|----------------|
| `is_low`-Flag = quantity ≤ `StockItem.LOW_STOCK_THRESHOLD` (10) | `StockItem.is_low`-Property |
| `is_out_of_stock`-Flag = quantity ≤ 0 | `StockItem.is_out_of_stock`-Property |
| Niedrigbestand-Abfrage nutzt DB-seitigen Filter für Performance | `SQLAlchemyStockRepository.list_low_stock()` |

---

## Alternativabläufe

### A1 — Medikament existiert nicht
- Schritt 1 beim Hinzufügen oder Ausgeben schlägt fehl.
- Antwort: `HTTP 404 { "detail": "Medication not found." }`

### A2 — Ausgabe übersteigt verfügbaren Bestand
- Schritt 3 beim Ausgeben: `quantity - amount < 0`.
- Antwort: `HTTP 422 { "detail": "Insufficient stock..." }`

### A3 — Kein Lagereintrag für Medikament vorhanden
- Schritt 2 beim Ausgeben: `StockRepository.get_by_medication()` gibt `None` zurück.
- Antwort: `HTTP 422 { "detail": "No stock entry found for medication '...'." }`

---

## Nachbedingungen

- **Hinzufügen**: `StockItem.quantity` um `amount` erhöht; Datensatz erstellt, falls erste Lieferung.
- **Ausgeben**: `StockItem.quantity` um `amount` reduziert; sinkt niemals unter null.

---

## Verwandte Use-Cases

- UC-001 — Termin buchen (keine Abhängigkeit; parallele Workflows)
