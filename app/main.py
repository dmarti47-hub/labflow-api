from fastapi import FastAPI

from app.database import check_database_connection
from app.settings import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Production-style REST API for tracking mock clinical lab sample workflows.",
)


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
