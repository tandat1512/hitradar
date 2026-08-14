"""
Common response schemas — Feature 3.2 FastAPI Backend.

Source: output_schema.json (canonical) + API-level metadata.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    field: str | None = None
    issue: str | None = None
    code: str | None = None


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    request_id: str | None = None
    details: list[ErrorDetail] = Field(default_factory=list)
    timestamp: str = Field(default_factory=_utc_now)

    model_config = {
        "json_schema_extra": {
            "example": {
                "error_code": "INVALID_FEATURE",
                "message": "Feature is not a valid canonical input field.",
                "request_id": None,
                "details": [],
                "timestamp": "2026-08-05T10:00:00Z",
            }
        }
    }


# ── Model Info ─────────────────────────────────────────────────────────────────

class Metrics(BaseModel):
    MAE: float | None = None
    RMSE: float | None = None
    R2: float | None = None

    model_config = {"extra": "forbid"}


class ModelInfoResponse(BaseModel):
    model_id: str
    model_version: str
    model_family: str
    package_version: str
    data_version: str
    feature_set: str
    training_date: str | None = None
    metrics: Metrics | None = None
    timestamp: str = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}


# ── Features ───────────────────────────────────────────────────────────────────

class FieldDescriptor(BaseModel):
    name: str
    position: int
    data_type: str
    required: bool
    minimum: float | None = None
    maximum: float | None = None
    allowed_categories: list[str] | None = None
    default_policy: str = "PIPELINE_IMPUTE"

    model_config = {"extra": "forbid"}


class FeaturesResponse(BaseModel):
    canonical_fields: list[FieldDescriptor]
    selected_features: list[str]
    total_input_fields: int
    total_selected_features: int
    timestamp: str = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}
