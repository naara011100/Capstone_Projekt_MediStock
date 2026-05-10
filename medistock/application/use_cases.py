"""
Application layer — use cases that orchestrate domain services and repositories.

Each use case class owns one workflow boundary.  Callers (routers, CLI, tests)
pass primitive IDs; the use case resolves them to domain objects internally and
delegates business logic to the domain services.

Exceptions raised:
  LookupError  — a referenced entity does not exist (→ HTTP 404)
  ValueError   — a business rule was violated (→ HTTP 422)
"""
from datetime import datetime
from uuid import UUID

from medistock.domain.services import BookingService, InventoryService


class BookingUseCase:
    """Orchestrates the full appointment-booking workflow.

    Responsibilities beyond BookingService:
    - Resolve patient / doctor / room IDs to domain objects before booking.
    - Provide a single dependency for all appointment operations so routers
      do not need to import three separate repositories.
    """

    def __init__(
        self,
        service: BookingService,
        patient_repo,
        doctor_repo,
        room_repo,
    ) -> None:
        self._service = service
        self._patient_repo = patient_repo
        self._doctor_repo = doctor_repo
        self._room_repo = room_repo

    # ── write operations ────────────────────────────────────────────────────

    def book(
        self,
        patient_id: UUID,
        doctor_id: UUID,
        room_id: UUID,
        scheduled_at: datetime,
        duration_minutes: int,
        notes: str = "",
    ):
        patient = self._patient_repo.get_by_id(patient_id)
        if patient is None:
            raise LookupError("Patient not found.")
        doctor = self._doctor_repo.get_by_id(doctor_id)
        if doctor is None:
            raise LookupError("Doctor not found.")
        room = self._room_repo.get_by_id(room_id)
        if room is None:
            raise LookupError("Room not found.")
        return self._service.book_appointment(
            patient, doctor, room, scheduled_at, duration_minutes, notes
        )

    def confirm(self, appointment_id: UUID):
        return self._service.confirm_appointment(appointment_id)

    def complete(self, appointment_id: UUID):
        return self._service.complete_appointment(appointment_id)

    def cancel(self, appointment_id: UUID):
        return self._service.cancel_appointment(appointment_id)

    def mark_no_show(self, appointment_id: UUID):
        return self._service.mark_no_show(appointment_id)

    # ── read operations ──────────────────────────────────────────────────────

    def get(self, appointment_id: UUID):
        return self._service.get_appointment(appointment_id)

    def list_all(self):
        return self._service._repo.list_all()

    def list_by_patient(self, patient_id: UUID):
        return self._service.list_appointments_by_patient(patient_id)

    def list_by_doctor(self, doctor_id: UUID):
        return self._service.list_appointments_by_doctor(doctor_id)


class InventoryUseCase:
    """Orchestrates medication stock management.

    Responsibilities beyond InventoryService:
    - Resolve medication IDs to domain objects before stock operations.
    - Single dependency for all inventory write operations.
    """

    def __init__(self, service: InventoryService, medication_repo) -> None:
        self._service = service
        self._medication_repo = medication_repo

    # ── write operations ────────────────────────────────────────────────────

    def add_stock(self, medication_id: UUID, amount: int, location: str):
        medication = self._medication_repo.get_by_id(medication_id)
        if medication is None:
            raise LookupError("Medication not found.")
        return self._service.add_stock(medication, amount, location)

    def dispense(self, medication_id: UUID, amount: int):
        medication = self._medication_repo.get_by_id(medication_id)
        if medication is None:
            raise LookupError("Medication not found.")
        return self._service.dispense(medication, amount)

    # ── read operations ──────────────────────────────────────────────────────

    def list_all_stock(self):
        return self._service.list_all_stock()

    def get_low_stock_alerts(self):
        return self._service.get_low_stock_alerts()
