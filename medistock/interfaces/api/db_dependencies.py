"""
FastAPI dependency providers that wire the SQLAlchemy infrastructure layer
into the API routers.

Usage — swap the imports in any router from:
    from medistock.interfaces.api.dependencies import get_patient_repository
to:
    from medistock.interfaces.api.db_dependencies import get_patient_repository

The DATABASE_URL environment variable controls which PostgreSQL instance is used
(defaults to postgresql://medistock:medistock@localhost:5432/medistock).
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from medistock.domain.services import BookingService, InventoryService
from medistock.infrastructure.database import get_db
from medistock.infrastructure.repositories.appointment_repository import SQLAlchemyAppointmentRepository
from medistock.infrastructure.repositories.doctor_repository import SQLAlchemyDoctorRepository
from medistock.infrastructure.repositories.medication_repository import SQLAlchemyMedicationRepository
from medistock.infrastructure.repositories.patient_repository import SQLAlchemyPatientRepository
from medistock.infrastructure.repositories.room_repository import SQLAlchemyRoomRepository
from medistock.infrastructure.repositories.stock_repository import SQLAlchemyStockRepository


def get_patient_repository(db: Session = Depends(get_db)) -> SQLAlchemyPatientRepository:
    return SQLAlchemyPatientRepository(db)


def get_doctor_repository(db: Session = Depends(get_db)) -> SQLAlchemyDoctorRepository:
    return SQLAlchemyDoctorRepository(db)


def get_room_repository(db: Session = Depends(get_db)) -> SQLAlchemyRoomRepository:
    return SQLAlchemyRoomRepository(db)


def get_medication_repository(db: Session = Depends(get_db)) -> SQLAlchemyMedicationRepository:
    return SQLAlchemyMedicationRepository(db)


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(SQLAlchemyAppointmentRepository(db))


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    return InventoryService(SQLAlchemyStockRepository(db))
