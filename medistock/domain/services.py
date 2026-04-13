from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
from .models.appointment import Appointment, AppointmentStatus
from .models.doctor import Doctor
from .models.medication import Medication
from .models.patient import Patient
from .models.room import Room
from .models.stock_item import StockItem

class AbstractAppointmentRepository(ABC):
    @abstractmethod
    def save(self, appointment: Appointment) -> None: ...
    @abstractmethod
    def get_by_id(self, appointment_id: UUID) -> Appointment | None: ...
    @abstractmethod
    def list_all(self) -> list[Appointment]: ...
    @abstractmethod
    def list_by_doctor(self, doctor_id: UUID) -> list[Appointment]: ...
    @abstractmethod
    def list_by_patient(self, patient_id: UUID) -> list[Appointment]: ...
    @abstractmethod
    def list_by_status(self, status: AppointmentStatus) -> list[Appointment]: ...

class AbstractStockRepository(ABC):
    @abstractmethod
    def save(self, stock_item: StockItem) -> None: ...
    @abstractmethod
    def get_by_id(self, stock_item_id: UUID) -> StockItem | None: ...
    @abstractmethod
    def get_by_medication(self, medication_id: UUID) -> StockItem | None: ...
    @abstractmethod
    def list_all(self) -> list[StockItem]: ...
    @abstractmethod
    def list_low_stock(self) -> list[StockItem]: ...

class BookingService:
    def __init__(self, appointment_repo: AbstractAppointmentRepository):
        self._repo = appointment_repo

    def book_appointment(self, patient, doctor, room, scheduled_at, duration_minutes, notes=""):
        appointment = Appointment(patient=patient, doctor=doctor, room=room,
                                  scheduled_at=scheduled_at, duration_minutes=duration_minutes, notes=notes)
        self._check_conflicts(appointment)
        self._repo.save(appointment)
        return appointment

    def confirm_appointment(self, appointment_id):
        appt = self._get_or_raise(appointment_id)
        appt.confirm()
        self._repo.save(appt)
        return appt

    def complete_appointment(self, appointment_id):
        appt = self._get_or_raise(appointment_id)
        appt.complete()
        self._repo.save(appt)
        return appt

    def cancel_appointment(self, appointment_id):
        appt = self._get_or_raise(appointment_id)
        appt.cancel()
        self._repo.save(appt)
        return appt

    def mark_no_show(self, appointment_id):
        appt = self._get_or_raise(appointment_id)
        appt.mark_no_show()
        self._repo.save(appt)
        return appt

    def get_appointment(self, appointment_id):
        return self._get_or_raise(appointment_id)

    def list_appointments_by_patient(self, patient_id):
        return self._repo.list_by_patient(patient_id)

    def list_appointments_by_doctor(self, doctor_id):
        return self._repo.list_by_doctor(doctor_id)

    def _check_conflicts(self, new_appt):
        active = {AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED}
        for existing in [a for a in self._repo.list_all() if a.status in active]:
            if not new_appt.overlaps_with(existing):
                continue
            if existing.doctor.id == new_appt.doctor.id:
                raise ValueError(f"Doctor '{new_appt.doctor.full_name}' already has an appointment at {existing.scheduled_at}.")
            if existing.patient.id == new_appt.patient.id:
                raise ValueError(f"Patient '{new_appt.patient.full_name}' already has an appointment at {existing.scheduled_at}.")
            if existing.room.id == new_appt.room.id:
                raise ValueError(f"Room '{new_appt.room.name}' is already booked at {existing.scheduled_at}.")

    def _get_or_raise(self, appointment_id):
        appt = self._repo.get_by_id(appointment_id)
        if not appt:
            raise ValueError(f"Appointment with id '{appointment_id}' not found.")
        return appt

class InventoryService:
    def __init__(self, stock_repo: AbstractStockRepository):
        self._repo = stock_repo

    def add_stock(self, medication, amount, location):
        item = self._repo.get_by_medication(medication.id)
        if item is None:
            item = StockItem(medication=medication, quantity=0, location=location)
        item.add_stock(amount)
        self._repo.save(item)
        return item

    def dispense(self, medication, amount):
        item = self._repo.get_by_medication(medication.id)
        if item is None:
            raise ValueError(f"No stock entry found for medication '{medication.name}'.")
        item.dispense(amount)
        self._repo.save(item)
        return item

    def get_stock(self, medication):
        return self._repo.get_by_medication(medication.id)

    def list_all_stock(self):
        return self._repo.list_all()

    def get_low_stock_alerts(self):
        return self._repo.list_low_stock()

    def is_out_of_stock(self, medication):
        item = self._repo.get_by_medication(medication.id)
        return item is None or item.is_out_of_stock
