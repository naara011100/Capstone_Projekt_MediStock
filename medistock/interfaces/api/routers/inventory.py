from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from medistock.application.use_cases import InventoryUseCase
from medistock.domain.models.medication import Medication
from medistock.infrastructure.repositories.base import DuplicateEntryError
from medistock.interfaces.api.db_dependencies import (
    get_inventory_use_case,
    get_medication_repository,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ---------- Medication schemas ----------

class MedicationCreate(BaseModel):
    name: str
    description: str
    unit: str


class MedicationResponse(BaseModel):
    id: UUID
    name: str
    description: str
    unit: str
    is_active: bool


class StockAddRequest(BaseModel):
    medication_id: UUID
    amount: int
    location: str


class StockDispenseRequest(BaseModel):
    medication_id: UUID
    amount: int


class StockItemResponse(BaseModel):
    id: UUID
    medication_id: UUID
    medication_name: str
    quantity: int
    location: str
    is_low: bool
    is_out_of_stock: bool


def _med_to_response(m: Medication) -> MedicationResponse:
    return MedicationResponse(
        id=m.id,
        name=m.name,
        description=m.description,
        unit=m.unit,
        is_active=m.is_active,
    )


def _stock_to_response(s) -> StockItemResponse:
    return StockItemResponse(
        id=s.id,
        medication_id=s.medication.id,
        medication_name=s.medication.name,
        quantity=s.quantity,
        location=s.location,
        is_low=s.is_low,
        is_out_of_stock=s.is_out_of_stock,
    )


# ---------- Medication endpoints (simple CRUD — no orchestration) ----------

@router.post("/medications", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(payload: MedicationCreate, repo=Depends(get_medication_repository)):
    try:
        med = Medication(name=payload.name, description=payload.description, unit=payload.unit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    try:
        repo.save(med)
    except DuplicateEntryError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A medication with this name already exists.")
    return _med_to_response(med)


@router.get("/medications", response_model=list[MedicationResponse])
def list_medications(repo=Depends(get_medication_repository)):
    return [_med_to_response(m) for m in repo.list_all()]


@router.get("/medications/{medication_id}", response_model=MedicationResponse)
def get_medication(medication_id: UUID, repo=Depends(get_medication_repository)):
    med = repo.get_by_id(medication_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found.")
    return _med_to_response(med)


# ---------- Stock endpoints (orchestrated via InventoryUseCase) ----------

@router.get("/stock", response_model=list[StockItemResponse])
def list_stock(use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return [_stock_to_response(s) for s in use_case.list_all_stock()]


@router.get("/stock/low-stock", response_model=list[StockItemResponse])
def list_low_stock(use_case: InventoryUseCase = Depends(get_inventory_use_case)):
    return [_stock_to_response(s) for s in use_case.get_low_stock_alerts()]


@router.post("/stock/add", response_model=StockItemResponse)
def add_stock(
    payload: StockAddRequest,
    use_case: InventoryUseCase = Depends(get_inventory_use_case),
):
    try:
        item = use_case.add_stock(payload.medication_id, payload.amount, payload.location)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _stock_to_response(item)


@router.post("/stock/dispense", response_model=StockItemResponse)
def dispense_stock(
    payload: StockDispenseRequest,
    use_case: InventoryUseCase = Depends(get_inventory_use_case),
):
    try:
        item = use_case.dispense(payload.medication_id, payload.amount)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _stock_to_response(item)
