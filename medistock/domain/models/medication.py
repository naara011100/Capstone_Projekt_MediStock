from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Medication:
    name: str
    description: str
    unit: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Medication name must not be empty.")
        if not self.unit.strip():
            raise ValueError("Medication unit must not be empty.")

    def deactivate(self):
        self.is_active = False
