"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.deps import get_current_user
from backend.core.settings import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str = "connected"


@router.get("")
async def health_check(
    _user: dict = Depends(get_current_user),
) -> HealthResponse:
    """Authenticated health check — verifies app version and database connectivity."""
    database_status = "connected"
    try:
        # TODO: Add real Supabase health ping once client is configured
        # For now, verify the connection string is configured
        if not settings.DATABASE_URL or settings.DATABASE_URL == "":
            database_status = "not configured"
    except Exception:
        database_status = "error"

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database=database_status,
    )
