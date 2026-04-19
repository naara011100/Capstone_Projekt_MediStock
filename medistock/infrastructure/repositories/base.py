"""
Shared helpers for SQLAlchemy repository implementations.

The _build_* functions reconstruct domain objects from ORM rows without
triggering __post_init__ validation.  This is intentional: data coming
out of the database was already validated on write; re-running creation-
time guards (e.g. "scheduled_at must be in the future") would incorrectly
reject perfectly valid historical records.
"""
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

class DuplicateEntryError(Exception):
    """Raised when a DB unique constraint is violated during save()."""


@contextmanager
def safe_commit(db: Session):
    """Commit the session; on IntegrityError roll back and raise DuplicateEntryError."""
    try:
        yield
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEntryError(str(exc.orig)) from exc


from medistock.domain.models.appointment import Appointment, AppointmentStatus
from medistock.domain.models.doctor import Doctor
from medistock.domain.models.medication import Medication
from medistock.domain.models.patient import Patient
from medistock.domain.models.room import Room
from medistock.domain.models.stock_item import StockItem
from medistock.infrastructure.orm.models import (
    AppointmentORM,
    DoctorORM,
    MedicationORM,
    PatientORM,
    RoomORM,
    StockItemORM,
)


# ---------------------------------------------------------------------------
# ORM → Domain
# ---------------------------------------------------------------------------

def build_patient(row: PatientORM) -> Patient:
    obj = object.__new__(Patient)
    obj.id = row.id
    obj.first_name = row.first_name
    obj.last_name = row.last_name
    obj.date_of_birth = row.date_of_birth
    obj.email = row.email
    obj.phone = row.phone
    obj.is_active = row.is_active
    obj.created_at = row.created_at
    return obj


def build_doctor(row: DoctorORM) -> Doctor:
    obj = object.__new__(Doctor)
    obj.id = row.id
    obj.first_name = row.first_name
    obj.last_name = row.last_name
    obj.specialization = row.specialization
    obj.email = row.email
    obj.phone = row.phone
    obj.is_active = row.is_active
    obj.created_at = row.created_at
    return obj


def build_room(row: RoomORM) -> Room:
    obj = object.__new__(Room)
    obj.id = row.id
    obj.name = row.name
    obj.floor = row.floor
    obj.capacity = row.capacity
    obj.is_available = row.is_available
    obj.created_at = row.created_at
    return obj


def build_medication(row: MedicationORM) -> Medication:
    obj = object.__new__(Medication)
    obj.id = row.id
    obj.name = row.name
    obj.description = row.description
    obj.unit = row.unit
    obj.is_active = row.is_active
    obj.created_at = row.created_at
    return obj


def build_stock_item(row: StockItemORM) -> StockItem:
    obj = object.__new__(StockItem)
    obj.id = row.id
    obj.medication = build_medication(row.medication)
    obj.quantity = row.quantity
    obj.location = row.location
    obj.low_stock_threshold = row.low_stock_threshold
    obj.created_at = row.created_at
    obj.updated_at = row.updated_at
    return obj


def build_appointment(row: AppointmentORM) -> Appointment:
    obj = object.__new__(Appointment)
    obj.id = row.id
    obj.patient = build_patient(row.patient)
    obj.doctor = build_doctor(row.doctor)
    obj.room = build_room(row.room)
    obj.scheduled_at = row.scheduled_at
    obj.duration_minutes = row.duration_minutes
    obj.status = AppointmentStatus(row.status)
    obj.notes = row.notes
    obj.created_at = row.created_at
    obj.updated_at = row.updated_at
    return obj


# ---------------------------------------------------------------------------
# Domain → ORM  (used by save())
# ---------------------------------------------------------------------------

def patient_to_orm(domain: Patient) -> PatientORM:
    return PatientORM(
        id=domain.id,
        first_name=domain.first_name,
        last_name=domain.last_name,
        date_of_birth=domain.date_of_birth,
        email=domain.email,
        phone=domain.phone,
        is_active=domain.is_active,
        created_at=domain.created_at,
    )


def doctor_to_orm(domain: Doctor) -> DoctorORM:
    return DoctorORM(
        id=domain.id,
        first_name=domain.first_name,
        last_name=domain.last_name,
        specialization=domain.specialization,
        email=domain.email,
        phone=domain.phone,
        is_active=domain.is_active,
        created_at=domain.created_at,
    )


def room_to_orm(domain: Room) -> RoomORM:
    return RoomORM(
        id=domain.id,
        name=domain.name,
        floor=domain.floor,
        capacity=domain.capacity,
        is_available=domain.is_available,
        created_at=domain.created_at,
    )


def medication_to_orm(domain: Medication) -> MedicationORM:
    return MedicationORM(
        id=domain.id,
        name=domain.name,
        description=domain.description,
        unit=domain.unit,
        is_active=domain.is_active,
        created_at=domain.created_at,
    )


def stock_item_to_orm(domain: StockItem) -> StockItemORM:
    return StockItemORM(
        id=domain.id,
        medication_id=domain.medication.id,
        quantity=domain.quantity,
        location=domain.location,
        low_stock_threshold=domain.low_stock_threshold,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def appointment_to_orm(domain: Appointment) -> AppointmentORM:
    return AppointmentORM(
        id=domain.id,
        patient_id=domain.patient.id,
        doctor_id=domain.doctor.id,
        room_id=domain.room.id,
        scheduled_at=domain.scheduled_at,
        duration_minutes=domain.duration_minutes,
        status=domain.status.value,
        notes=domain.notes,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )
