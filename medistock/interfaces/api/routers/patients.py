from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from medistock.domain.models.patient import Patient
from medistock.infrastructure.repositories.base import DuplicateEntryError
from medistock.interfaces.api.db_dependencies import get_patient_repository

router = APIRouter(prefix="/patients", tags=["Patients"])


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    email: EmailStr
    phone: str


class PatientResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date
    email: str
    phone: str
    is_active: bool

    model_config = {"from_attributes": True}


def _to_response(p: Patient) -> PatientResponse:
    return PatientResponse(
        id=p.id,
        first_name=p.first_name,
        last_name=p.last_name,
        full_name=p.full_name,
        date_of_birth=p.date_of_birth,
        email=p.email,
        phone=p.phone,
        is_active=p.is_active,
    )


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, repo=Depends(get_patient_repository)):
    try:
        patient = Patient(
            first_name=payload.first_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
            email=payload.email,
            phone=payload.phone,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    try:
        repo.save(patient)
    except DuplicateEntryError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A patient with this email already exists.")
    return _to_response(patient)


@router.get("/", response_model=list[PatientResponse])
def list_patients(repo=Depends(get_patient_repository)):
    return [_to_response(p) for p in repo.list_all()]


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: UUID, repo=Depends(get_patient_repository)):
    patient = repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    return _to_response(patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_patient(patient_id: UUID, repo=Depends(get_patient_repository)):
    patient = repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    patient.deactivate()
    repo.save(patient)
