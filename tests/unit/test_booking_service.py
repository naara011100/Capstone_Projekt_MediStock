"""
Unit tests for BookingService.

All repository interactions are replaced with MagicMock — no database required.
"""
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

from medistock.domain.models.appointment import Appointment, AppointmentStatus
from medistock.domain.models.doctor import Doctor
from medistock.domain.models.patient import Patient
from medistock.domain.models.room import Room
from medistock.domain.services import BookingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def future(hours: float = 2.0) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)


def make_patient(email: str = "p@test.de") -> Patient:
    return Patient(
        first_name="Anna", last_name="Test",
        date_of_birth=date(1990, 1, 1),
        email=email, phone="0000",
    )


def make_doctor(email: str = "d@test.de") -> Doctor:
    return Doctor(
        first_name="Max", last_name="Test",
        specialization="Cardiology",
        email=email, phone="1111",
    )


def make_room(name: str = "101") -> Room:
    return Room(name=name, floor=1, capacity=2)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.list_all.return_value = []
    return repo


@pytest.fixture
def service(mock_repo):
    return BookingService(mock_repo)


@pytest.fixture
def patient():
    return make_patient()


@pytest.fixture
def doctor():
    return make_doctor()


@pytest.fixture
def room():
    return make_room()


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

def test_book_appointment_returns_scheduled(service, mock_repo, patient, doctor, room):
    appt = service.book_appointment(patient, doctor, room, future(), 60)

    assert appt.status == AppointmentStatus.SCHEDULED
    assert appt.patient is patient
    assert appt.doctor is doctor
    assert appt.room is room
    mock_repo.save.assert_called_once_with(appt)


def test_book_appointment_with_notes(service, patient, doctor, room):
    appt = service.book_appointment(patient, doctor, room, future(), 30, notes="Follow-up")
    assert appt.notes == "Follow-up"


def test_book_appointment_past_time_raises(service, patient, doctor, room):
    past = datetime.utcnow() - timedelta(hours=1)
    with pytest.raises(ValueError, match="future"):
        service.book_appointment(patient, doctor, room, past, 30)


def test_book_appointment_zero_duration_raises(service, patient, doctor, room):
    with pytest.raises(ValueError, match="positive"):
        service.book_appointment(patient, doctor, room, future(), 0)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _booked_appointment(patient, doctor, room, start_hours=2, duration=60):
    """Helper: create a SCHEDULED appointment (bypasses __post_init__)."""
    appt = Appointment(
        patient=patient, doctor=doctor, room=room,
        scheduled_at=future(start_hours), duration_minutes=duration,
    )
    return appt


def test_doctor_conflict_raises(service, mock_repo, patient, doctor, room):
    other_patient = make_patient("other@test.de")
    other_room = make_room("102")
    existing = _booked_appointment(other_patient, doctor, other_room)
    mock_repo.list_all.return_value = [existing]

    with pytest.raises(ValueError, match="already has an appointment"):
        service.book_appointment(patient, doctor, other_room, future(2), 30)


def test_patient_conflict_raises(service, mock_repo, patient, doctor, room):
    other_doctor = make_doctor("other@doc.de")
    other_room = make_room("102")
    existing = _booked_appointment(patient, other_doctor, other_room)
    mock_repo.list_all.return_value = [existing]

    with pytest.raises(ValueError, match="already has an appointment"):
        service.book_appointment(patient, doctor, other_room, future(2), 30)


def test_room_conflict_raises(service, mock_repo, patient, doctor, room):
    other_patient = make_patient("other@test.de")
    other_doctor = make_doctor("other@doc.de")
    existing = _booked_appointment(other_patient, other_doctor, room)
    mock_repo.list_all.return_value = [existing]

    with pytest.raises(ValueError, match="already booked"):
        service.book_appointment(patient, doctor, room, future(2), 30)


def test_no_conflict_when_times_do_not_overlap(service, mock_repo, patient, doctor, room):
    # existing: 2-3 h from now, new: 4-5 h from now → no overlap
    existing = _booked_appointment(patient, doctor, room, start_hours=2, duration=60)
    mock_repo.list_all.return_value = [existing]

    appt = service.book_appointment(patient, doctor, room, future(4), 60)
    assert appt.status == AppointmentStatus.SCHEDULED


def test_cancelled_appointment_ignored_in_conflict_check(service, mock_repo, patient, doctor, room):
    existing = _booked_appointment(patient, doctor, room, start_hours=2, duration=60)
    existing.cancel()
    mock_repo.list_all.return_value = [existing]

    # Should NOT raise — cancelled appointments are excluded from conflict check
    appt = service.book_appointment(patient, doctor, room, future(2), 30)
    assert appt is not None


# ---------------------------------------------------------------------------
# State transitions
# ---------------------------------------------------------------------------

def test_confirm_appointment(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    mock_repo.get_by_id.return_value = appt

    result = service.confirm_appointment(appt.id)

    assert result.status == AppointmentStatus.CONFIRMED
    mock_repo.save.assert_called_with(appt)


def test_complete_appointment(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    appt.confirm()
    mock_repo.get_by_id.return_value = appt

    result = service.complete_appointment(appt.id)

    assert result.status == AppointmentStatus.COMPLETED


def test_cancel_appointment(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    mock_repo.get_by_id.return_value = appt

    result = service.cancel_appointment(appt.id)

    assert result.status == AppointmentStatus.CANCELLED


def test_mark_no_show(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    appt.confirm()
    mock_repo.get_by_id.return_value = appt

    result = service.mark_no_show(appt.id)

    assert result.status == AppointmentStatus.NO_SHOW


def test_confirm_already_confirmed_raises(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    appt.confirm()
    mock_repo.get_by_id.return_value = appt

    with pytest.raises(ValueError, match="SCHEDULED"):
        service.confirm_appointment(appt.id)


def test_complete_unconfirmed_raises(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    mock_repo.get_by_id.return_value = appt

    with pytest.raises(ValueError, match="CONFIRMED"):
        service.complete_appointment(appt.id)


def test_cancel_completed_raises(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    appt.confirm()
    appt.complete()
    mock_repo.get_by_id.return_value = appt

    with pytest.raises(ValueError, match="Cannot cancel"):
        service.cancel_appointment(appt.id)


def test_no_show_unconfirmed_raises(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    mock_repo.get_by_id.return_value = appt

    with pytest.raises(ValueError, match="CONFIRMED"):
        service.mark_no_show(appt.id)


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------

def test_get_appointment_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="not found"):
        service.get_appointment(uuid4())


def test_list_by_patient(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    mock_repo.list_by_patient.return_value = [appt]

    results = service.list_appointments_by_patient(patient.id)

    assert len(results) == 1
    mock_repo.list_by_patient.assert_called_once_with(patient.id)


def test_list_by_doctor(service, mock_repo, patient, doctor, room):
    appt = _booked_appointment(patient, doctor, room)
    mock_repo.list_by_doctor.return_value = [appt]

    results = service.list_appointments_by_doctor(doctor.id)

    assert len(results) == 1
    mock_repo.list_by_doctor.assert_called_once_with(doctor.id)
