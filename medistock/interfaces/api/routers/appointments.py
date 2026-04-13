from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from medistock.domain.models.appointment import AppointmentStatus
from medistock.interfaces.api.dependencies import (
    get_booking_service,
    get_patient_repository,
    get_doctor_repository,
    get_room_repository,
)

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
    service=Depends(get_booking_service),
    patient_repo=Depends(get_patient_repository),
    doctor_repo=Depends(get_doctor_repository),
    room_repo=Depends(get_room_repository),
):
    patient = patient_repo.get_by_id(payload.patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    doctor = doctor_repo.get_by_id(payload.doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")
    room = room_repo.get_by_id(payload.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")

    try:
        appt = service.book_appointment(
            patient=patient,
            doctor=doctor,
            room=room,
            scheduled_at=payload.scheduled_at,
            duration_minutes=payload.duration_minutes,
            notes=payload.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(service=Depends(get_booking_service)):
    return [_to_response(a) for a in service._repo.list_all()]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: UUID, service=Depends(get_booking_service)):
    try:
        appt = service.get_appointment(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(appointment_id: UUID, service=Depends(get_booking_service)):
    try:
        appt = service.confirm_appointment(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(appointment_id: UUID, service=Depends(get_booking_service)):
    try:
        appt = service.complete_appointment(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: UUID, service=Depends(get_booking_service)):
    try:
        appt = service.cancel_appointment(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)


@router.patch("/{appointment_id}/no-show", response_model=AppointmentResponse)
def mark_no_show(appointment_id: UUID, service=Depends(get_booking_service)):
    try:
        appt = service.mark_no_show(appointment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(appt)
