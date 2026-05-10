from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from medistock.interfaces.api.routers.patients import router as patients_router
from medistock.interfaces.api.routers.appointments import router as appointments_router
from medistock.interfaces.api.routers.inventory import router as inventory_router
from medistock.interfaces.api.routers.doctors_rooms import doctors_router, rooms_router

STATIC_DIR = Path(__file__).parent.parent / "web" / "static"

app = FastAPI(title="MediStock API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(patients_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(appointments_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")


@app.get("/ui", include_in_schema=False)
def ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "medistock"}
