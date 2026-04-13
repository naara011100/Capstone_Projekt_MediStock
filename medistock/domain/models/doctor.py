from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Doctor:
    first_name: str
    last_name: str
    specialization: str
    email: str
    phone: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.first_name.strip():
            raise ValueError("First name must not be empty.")
        if not self.last_name.strip():
            raise ValueError("Last name must not be empty.")
        if not self.specialization.strip():
            raise ValueError("Specialization must not be empty.")
        if "@" not in self.email:
            raise ValueError(f"Invalid email address: {self.email}")

    @property
    def full_name(self) -> str:
        return f"Dr. {self.first_name} {self.last_name}"

    def deactivate(self):
        self.is_active = False
