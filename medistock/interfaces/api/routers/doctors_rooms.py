from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from medistock.domain.models.doctor import Doctor
from medistock.domain.models.room import Room
from medistock.infrastructure.repositories.base import DuplicateEntryError
from medistock.interfaces.api.db_dependencies import get_doctor_repository, get_room_repository

doctors_router = APIRouter(prefix="/doctors", tags=["Doctors"])
rooms_router = APIRouter(prefix="/rooms", tags=["Rooms"])


# ---------- Doctor schemas ----------

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    email: EmailStr
    phone: str


class DoctorResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    full_name: str
    specialization: str
    email: str
    phone: str
    is_active: bool


def _doctor_to_response(d: Doctor) -> DoctorResponse:
    return DoctorResponse(
        id=d.id,
        first_name=d.first_name,
        last_name=d.last_name,
        full_name=d.full_name,
        specialization=d.specialization,
        email=d.email,
        phone=d.phone,
        is_active=d.is_active,
    )


@doctors_router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, repo=Depends(get_doctor_repository)):
    try:
        doctor = Doctor(
            first_name=payload.first_name,
            last_name=payload.last_name,
            specialization=payload.specialization,
            email=payload.email,
            phone=payload.phone,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    try:
        repo.save(doctor)
    except DuplicateEntryError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A doctor with this email already exists.")
    return _doctor_to_response(doctor)


@doctors_router.get("/", response_model=list[DoctorResponse])
def list_doctors(repo=Depends(get_doctor_repository)):
    return [_doctor_to_response(d) for d in repo.list_all()]


@doctors_router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: UUID, repo=Depends(get_doctor_repository)):
    doctor = repo.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")
    return _doctor_to_response(doctor)


@doctors_router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_doctor(doctor_id: UUID, repo=Depends(get_doctor_repository)):
    doctor = repo.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")
    doctor.deactivate()
    repo.save(doctor)


# ---------- Room schemas ----------

class RoomCreate(BaseModel):
    name: str
    floor: int
    capacity: int


class RoomResponse(BaseModel):
    id: UUID
    name: str
    floor: int
    capacity: int
    is_available: bool


def _room_to_response(r: Room) -> RoomResponse:
    return RoomResponse(
        id=r.id,
        name=r.name,
        floor=r.floor,
        capacity=r.capacity,
        is_available=r.is_available,
    )


@rooms_router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, repo=Depends(get_room_repository)):
    try:
        room = Room(name=payload.name, floor=payload.floor, capacity=payload.capacity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    try:
        repo.save(room)
    except DuplicateEntryError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A room with this name already exists.")
    return _room_to_response(room)


@rooms_router.get("/", response_model=list[RoomResponse])
def list_rooms(repo=Depends(get_room_repository)):
    return [_room_to_response(r) for r in repo.list_all()]


@rooms_router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: UUID, repo=Depends(get_room_repository)):
    room = repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    return _room_to_response(room)


@rooms_router.patch("/{room_id}/available", response_model=RoomResponse)
def set_room_available(room_id: UUID, repo=Depends(get_room_repository)):
    room = repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    room.mark_available()
    repo.save(room)
    return _room_to_response(room)


@rooms_router.patch("/{room_id}/unavailable", response_model=RoomResponse)
def set_room_unavailable(room_id: UUID, repo=Depends(get_room_repository)):
    room = repo.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found.")
    room.mark_unavailable()
    repo.save(room)
    return _room_to_response(room)
