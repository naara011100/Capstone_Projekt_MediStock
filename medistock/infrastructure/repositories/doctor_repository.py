from uuid import UUID

from sqlalchemy.orm import Session

from medistock.domain.models.doctor import Doctor
from medistock.infrastructure.orm.models import DoctorORM
from medistock.infrastructure.repositories.base import build_doctor, doctor_to_orm, safe_commit


class SQLAlchemyDoctorRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, doctor: Doctor) -> None:
        with safe_commit(self._db):
            self._db.merge(doctor_to_orm(doctor))

    def get_by_id(self, doctor_id: UUID) -> Doctor | None:
        row = self._db.get(DoctorORM, doctor_id)
        return build_doctor(row) if row else None

    def list_all(self) -> list[Doctor]:
        rows = self._db.query(DoctorORM).all()
        return [build_doctor(r) for r in rows]
