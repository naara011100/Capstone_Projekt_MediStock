from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from medistock.interfaces.api.routers.patients import router as patients_router
from medistock.interfaces.api.routers.appointments import router as appointments_router
from medistock.interfaces.api.routers.inventory import router as inventory_router
from medistock.interfaces.api.routers.doctors_rooms import doctors_router, rooms_router

app = FastAPI(title="MediStock API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(patients_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "medistock"}
