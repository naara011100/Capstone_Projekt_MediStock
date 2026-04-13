from uuid import UUID

from sqlalchemy.orm import Session

from medistock.domain.models.patient import Patient
from medistock.infrastructure.orm.models import PatientORM
from medistock.infrastructure.repositories.base import build_patient, patient_to_orm


class SQLAlchemyPatientRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, patient: Patient) -> None:
        self._db.merge(patient_to_orm(patient))
        self._db.commit()

    def get_by_id(self, patient_id: UUID) -> Patient | None:
        row = self._db.get(PatientORM, patient_id)
        return build_patient(row) if row else None

    def list_all(self) -> list[Patient]:
        rows = self._db.query(PatientORM).all()
        return [build_patient(r) for r in rows]
