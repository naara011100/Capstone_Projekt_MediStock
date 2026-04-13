from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Room:
    name: str
    floor: int
    capacity: int
    id: UUID = field(default_factory=uuid4)
    is_available: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Room name must not be empty.")
        if self.capacity <= 0:
            raise ValueError("Room capacity must be a positive integer.")

    def mark_unavailable(self):
        self.is_available = False

    def mark_available(self):
        self.is_available = True
