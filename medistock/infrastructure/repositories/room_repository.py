from uuid import UUID

from sqlalchemy.orm import Session

from medistock.domain.models.room import Room
from medistock.infrastructure.orm.models import RoomORM
from medistock.infrastructure.repositories.base import build_room, room_to_orm


class SQLAlchemyRoomRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, room: Room) -> None:
        self._db.merge(room_to_orm(room))
        self._db.commit()

    def get_by_id(self, room_id: UUID) -> Room | None:
        row = self._db.get(RoomORM, room_id)
        return build_room(row) if row else None

    def list_all(self) -> list[Room]:
        rows = self._db.query(RoomORM).all()
        return [build_room(r) for r in rows]
