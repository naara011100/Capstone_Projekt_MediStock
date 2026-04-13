from uuid import UUID

from sqlalchemy.orm import Session

from medistock.domain.models.appointment import Appointment, AppointmentStatus
from medistock.domain.services import AbstractAppointmentRepository
from medistock.infrastructure.orm.models import AppointmentORM
from medistock.infrastructure.repositories.base import appointment_to_orm, build_appointment


class SQLAlchemyAppointmentRepository(AbstractAppointmentRepository):
    """
    Concrete implementation of AbstractAppointmentRepository backed by PostgreSQL.

    session.merge() handles both INSERT (new record) and UPDATE (existing record)
    keyed on the primary key, matching the save-or-update semantics expected by
    BookingService.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def save(self, appointment: Appointment) -> None:
        self._db.merge(appointment_to_orm(appointment))
        self._db.commit()

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        row = self._db.get(AppointmentORM, appointment_id)
        return build_appointment(row) if row else None

    def list_all(self) -> list[Appointment]:
        rows = self._db.query(AppointmentORM).all()
        return [build_appointment(r) for r in rows]

    def list_by_doctor(self, doctor_id: UUID) -> list[Appointment]:
        rows = (
            self._db.query(AppointmentORM)
            .filter(AppointmentORM.doctor_id == doctor_id)
            .all()
        )
        return [build_appointment(r) for r in rows]

    def list_by_patient(self, patient_id: UUID) -> list[Appointment]:
        rows = (
            self._db.query(AppointmentORM)
            .filter(AppointmentORM.patient_id == patient_id)
            .all()
        )
        return [build_appointment(r) for r in rows]

    def list_by_status(self, status: AppointmentStatus) -> list[Appointment]:
        rows = (
            self._db.query(AppointmentORM)
            .filter(AppointmentORM.status == status.value)
            .all()
        )
        return [build_appointment(r) for r in rows]
