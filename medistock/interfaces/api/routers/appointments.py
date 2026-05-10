from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from medistock.application.use_cases import BookingUseCase
from medistock.domain.models.appointment import AppointmentStatus
from medistock.interfaces.api.db_dependencies import get_booking_use_case

router = APIRouter(prefix="/appointments", tags=["Appointments"])


class AppointmentCreate(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    room_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    notes: str = ""


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    patient_name: str
    doctor_id: UUID
    doctor_name: str
    room_id: UUID
    room_name: str
    scheduled_at: datetime
    duration_minutes: int
    status: AppointmentStatus
    notes: str


def _to_response(appt) -> AppointmentResponse:
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient.id,
        patient_name=appt.patient.full_name,
        doctor_id=appt.doctor.id,
        doctor_name=appt.doctor.full_name,
        room_id=appt.room.id,
        room_name=appt.room.name,
        scheduled_at=appt.scheduled_at,
        duration_minutes=appt.duration_minutes,
        status=appt.status,
        notes=appt.notes,
    )


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    use_case: BookingUseCase = Depends(get_booking_use_case),
):
    try:
        appt = use_case.book(
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
            room_id=payload.room_id,
            scheduled_at=payload.scheduled_at,
            duration_minutes=payload.duration_minutes,
            notes=payload.notes,
        )
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(use_case: BookingUseCase = Depends(get_booking_use_case)):
    return [_to_response(a) for a in use_case.list_all()]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: UUID,
    use_case: BookingUseCase = Depends(get_booking_use_case),
):
    try:
        appt = use_case.get(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(
    appointment_id: UUID,
    use_case: BookingUseCase = Depends(get_booking_use_case),
):
    try:
        appt = use_case.confirm(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: UUID,
    use_case: BookingUseCase = Depends(get_booking_use_case),
):
    try:
        appt = use_case.complete(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: UUID,
    use_case: BookingUseCase = Depends(get_booking_use_case),
):
    try:
        appt = use_case.cancel(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/no-show", response_model=AppointmentResponse)
def mark_no_show(
    appointment_id: UUID,
    use_case: BookingUseCase = Depends(get_booking_use_case),
):
    try:
        appt = use_case.mark_no_show(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)
