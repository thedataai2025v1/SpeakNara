"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.settings import settings

router = APIRouter()


class ServiceStatus(BaseModel):
    """Per-service health status."""
    database: str
    llm: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: ServiceStatus


@router.get("")
async def health_check() -> HealthResponse:
    """Health check — no auth required, reports service connectivity."""
    database_status: str = "connected"
    try:
        if not settings.database_url:
            database_status = "not configured"
    except Exception:
        database_status = "error"

    llm_status: str = "connected"
    try:
        if not settings.euri_api_key:
            llm_status = "not configured"
    except Exception:
        llm_status = "error"

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services=ServiceStatus(database=database_status, llm=llm_status),
    )
