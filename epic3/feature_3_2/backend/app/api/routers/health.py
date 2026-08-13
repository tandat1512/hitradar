"""
GET /health endpoint — Feature 3.2 FastAPI Backend Phase 3.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core import config
from app.services.pipeline_loader import PipelineLoader


router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str = Field(description="'healthy', 'degraded', or 'unavailable'")
    service_name: str = Field(default=config.APP_NAME)
    api_version: str = Field(default=config.APP_VERSION)
    model_loaded: bool = Field(description="True when pipeline is fully loaded")
    model_ready: bool = Field(description="Alias for model_loaded")
    explain_service_available: bool = Field(default=True)
    what_if_available: bool = Field(default=True)
    model_version: str | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    model_config = {"extra": "forbid"}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Service health check — liveness + readiness.

    Returns "healthy" when model pipeline is loaded.
    Returns "degraded" when model is not loaded (app started but loading pending).
    Never runs full prediction — only checks PipelineLoader singleton state.
    """
    pl = PipelineLoader.get_instance()
    model_loaded = pl is not None and pl.is_loaded()
    model_version: str | None = None

    if model_loaded:
        try:
            model_version = pl.get_model_version()
        except Exception:
            pass

    if model_loaded:
        status = "healthy"
    elif pl is not None:
        status = "degraded"
    else:
        status = "unavailable"

    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        model_ready=model_loaded,
        model_version=model_version,
    )
