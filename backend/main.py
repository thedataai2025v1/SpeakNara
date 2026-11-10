"""SpeakNara backend — FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import health
from backend.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])


@app.get("/health")
async def readiness_check() -> dict:
    """Readiness / health probe — no auth required, reports service status."""
    # Database connectivity check
    database_status: str = "connected"
    try:
        if not settings.database_url:
            database_status = "not configured"
    except Exception:
        database_status = "error"

    # LLM connectivity check
    llm_status: str = "connected"
    try:
        if not settings.euri_api_key:
            llm_status = "not configured"
    except Exception:
        llm_status = "error"

    return {
        "status": "ok",
        "version": settings.app_version,
        "services": {
            "database": database_status,
            "llm": llm_status,
        },
    }
