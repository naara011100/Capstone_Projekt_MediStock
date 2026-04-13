from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from .medication import Medication

LOW_STOCK_THRESHOLD = 10

@dataclass
class StockItem:
    medication: Medication
    quantity: int
    location: str
    id: UUID = field(default_factory=uuid4)
    low_stock_threshold: int = LOW_STOCK_THRESHOLD
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Stock quantity must not be negative.")
        if not self.location.strip():
            raise ValueError("Storage location must not be empty.")

    def add_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount to add must be greater than zero.")
        self.quantity += amount
        self.updated_at = datetime.utcnow()

    def dispense(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount to dispense must be greater than zero.")
        if self.quantity - amount < 0:
            raise ValueError(f"Insufficient stock for '{self.medication.name}'. Available: {self.quantity}, requested: {amount}.")
        self.quantity -= amount
        self.updated_at = datetime.utcnow()

    @property
    def is_low(self) -> bool:
        return self.quantity <= self.low_stock_threshold

    @property
    def is_out_of_stock(self) -> bool:
        return self.quantity == 0
