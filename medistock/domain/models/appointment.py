from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
from .doctor import Doctor
from .patient import Patient
from .room import Room

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

@dataclass
class Appointment:
    patient: Patient
    doctor: Doctor
    room: Room
    scheduled_at: datetime
    duration_minutes: int
    id: UUID = field(default_factory=uuid4)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.scheduled_at <= datetime.utcnow():
            raise ValueError("Appointment must be scheduled in the future.")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes.")

    @property
    def end_time(self) -> datetime:
        return self.scheduled_at + timedelta(minutes=self.duration_minutes)

    def confirm(self):
        if self.status != AppointmentStatus.SCHEDULED:
            raise ValueError("Only SCHEDULED appointments can be confirmed.")
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.utcnow()

    def complete(self):
        if self.status != AppointmentStatus.CONFIRMED:
            raise ValueError("Only CONFIRMED appointments can be completed.")
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def cancel(self):
        if self.status in (AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED):
            raise ValueError(f"Cannot cancel an appointment with status '{self.status}'.")
        self.status = AppointmentStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def mark_no_show(self):
        if self.status != AppointmentStatus.CONFIRMED:
            raise ValueError("Only CONFIRMED appointments can be marked as no-show.")
        self.status = AppointmentStatus.NO_SHOW
        self.updated_at = datetime.utcnow()

    def overlaps_with(self, other: "Appointment") -> bool:
        return self.scheduled_at < other.end_time and self.end_time > other.scheduled_at
