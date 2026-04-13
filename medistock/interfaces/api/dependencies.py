from medistock.domain.services import BookingService, InventoryService

class _InMemoryRepo:
    def __init__(self):
        self._store = {}
    def save(self, entity):
        self._store[entity.id] = entity
    def get_by_id(self, entity_id):
        return self._store.get(entity_id)
    def list_all(self):
        return list(self._store.values())

class _InMemoryAppointmentRepo(_InMemoryRepo):
    def list_by_doctor(self, doctor_id):
        return [a for a in self._store.values() if a.doctor.id == doctor_id]
    def list_by_patient(self, patient_id):
        return [a for a in self._store.values() if a.patient.id == patient_id]
    def list_by_status(self, status):
        return [a for a in self._store.values() if a.status == status]

class _InMemoryStockRepo(_InMemoryRepo):
    def get_by_medication(self, medication_id):
        return next((s for s in self._store.values() if s.medication.id == medication_id), None)
    def list_low_stock(self):
        return [s for s in self._store.values() if s.is_low]

_patient_repo = _InMemoryRepo()
_doctor_repo = _InMemoryRepo()
_room_repo = _InMemoryRepo()
_medication_repo = _InMemoryRepo()
_appointment_repo = _InMemoryAppointmentRepo()
_stock_repo = _InMemoryStockRepo()

def get_patient_repository(): return _patient_repo
def get_doctor_repository(): return _doctor_repo
def get_room_repository(): return _room_repo
def get_medication_repository(): return _medication_repo
def get_booking_service(): return BookingService(_appointment_repo)
def get_inventory_service(): return InventoryService(_stock_repo)
