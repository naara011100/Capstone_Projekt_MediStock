from uuid import UUID

from sqlalchemy.orm import Session

from medistock.domain.models.stock_item import StockItem
from medistock.domain.services import AbstractStockRepository
from medistock.infrastructure.orm.models import StockItemORM
from medistock.infrastructure.repositories.base import build_stock_item, stock_item_to_orm, safe_commit


class SQLAlchemyStockRepository(AbstractStockRepository):
    """
    Concrete implementation of AbstractStockRepository backed by PostgreSQL.

    list_low_stock() delegates the threshold comparison to the database so
    the query scales regardless of stock table size.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def save(self, stock_item: StockItem) -> None:
        with safe_commit(self._db):
            self._db.merge(stock_item_to_orm(stock_item))

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_by_id(self, stock_item_id: UUID) -> StockItem | None:
        row = self._db.get(StockItemORM, stock_item_id)
        return build_stock_item(row) if row else None

    def get_by_medication(self, medication_id: UUID) -> StockItem | None:
        row = (
            self._db.query(StockItemORM)
            .filter(StockItemORM.medication_id == medication_id)
            .first()
        )
        return build_stock_item(row) if row else None

    def list_all(self) -> list[StockItem]:
        rows = self._db.query(StockItemORM).all()
        return [build_stock_item(r) for r in rows]

    def list_low_stock(self) -> list[StockItem]:
        rows = (
            self._db.query(StockItemORM)
            .filter(StockItemORM.quantity <= StockItemORM.low_stock_threshold)
            .all()
        )
        return [build_stock_item(r) for r in rows]
