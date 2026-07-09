from fastapi import FastAPI

from app.database import check_database_connection
from app.routers.audit_logs import router as audit_logs_router
from app.routers.qc_notes import router as qc_notes_router
from app.routers.reports import router as reports_router
from app.routers.samples import router as samples_router
from app.settings import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Production-style REST API for tracking mock clinical lab sample workflows.",
)


app.include_router(samples_router)
app.include_router(qc_notes_router)
app.include_router(audit_logs_router)
app.include_router(reports_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to LabFlow API",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/health/db")
def database_health_check():
    check_database_connection()
    return {
        "status": "ok",
        "database": "connected",
    }
