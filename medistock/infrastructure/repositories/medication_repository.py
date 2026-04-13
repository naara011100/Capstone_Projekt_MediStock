from uuid import UUID

from sqlalchemy.orm import Session

from medistock.domain.models.medication import Medication
from medistock.infrastructure.orm.models import MedicationORM
from medistock.infrastructure.repositories.base import build_medication, medication_to_orm


class SQLAlchemyMedicationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, medication: Medication) -> None:
        self._db.merge(medication_to_orm(medication))
        self._db.commit()

    def get_by_id(self, medication_id: UUID) -> Medication | None:
        row = self._db.get(MedicationORM, medication_id)
        return build_medication(row) if row else None

    def list_all(self) -> list[Medication]:
        rows = self._db.query(MedicationORM).all()
        return [build_medication(r) for r in rows]
