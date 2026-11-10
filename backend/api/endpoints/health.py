"""Health check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from backend.core import settings

router = APIRouter()


@router.get("")
async def health_check() -> dict[str, str]:
    """Simple health check — returns status and version."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }
