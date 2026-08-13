"""
Pydantic models — EPIC 3 FastAPI Backend
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ── /predict & /explain request ──────────────────────────────────────────────

class PredictRequest(BaseModel):
    duration_min: float = Field(..., ge=0.0, le=120.0)
    explicit: bool
    release_year: int = Field(..., ge=1900, le=2100)
    release_month: float = Field(..., ge=1.0, le=12.0)
    decade: int = Field(..., ge=1900, le=2100)
    release_precision: str = Field(..., pattern=r"^(day|month|year)$")
    danceability: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    key: int = Field(..., ge=0, le=11)
    loudness: float = Field(..., ge=-60.0, le=0.0)
    mode: int = Field(..., ge=0, le=1)
    speechiness: float = Field(..., ge=0.0, le=1.0)
    acousticness: float = Field(..., ge=0.0, le=1.0)
    instrumentalness: float = Field(..., ge=0.0, le=1.0)
    liveness: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=0.0, le=1.0)
    tempo: float = Field(..., ge=0.0, le=300.0)
    time_signature: float = Field(...)

    model_config = {"extra": "allow"}


# ── /predict response ─────────────────────────────────────────────────────────

class PredictResponse(BaseModel):
    status: str
    prediction_raw: float
    prediction_clipped: float
    prediction_display: int
    warnings: list[str]
    model_id: str
    model_version: str
    package_version: str
    timestamp: str


# ── /explain response ─────────────────────────────────────────────────────────

class TopFeature(BaseModel):
    name: str
    shap_value: float
    feature_value: float | str


class ExplainResponse(BaseModel):
    status: str
    prediction_raw: float
    prediction_clipped: float
    prediction_display: int
    base_value: float
    shap_values: dict[str, float]
    top_features: list[TopFeature]
    model_id: str
    model_version: str
    timestamp: str


# ── /what-if request ──────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    base_features: PredictRequest
    changed_features: dict[str, float | bool | int | str] = Field(..., min_length=1)

    model_config = {"extra": "allow"}


# ── /what-if response ────────────────────────────────────────────────────────

class PredictionShort(BaseModel):
    prediction_raw: float
    prediction_clipped: float
    prediction_display: int


class WhatIfResponse(BaseModel):
    status: str
    prediction_before: PredictionShort
    prediction_after: PredictionShort
    delta: float
    delta_display: int
    changes_applied: dict[str, float | bool | int | str]
    model_id: str
    model_version: str
    timestamp: str


# ── /health response ──────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str


# ── /model-info response ──────────────────────────────────────────────────────

class Metrics(BaseModel):
    MAE: float | None = None
    RMSE: float | None = None
    R2: float | None = None


class ModelInfoResponse(BaseModel):
    model_id: str
    model_version: str
    model_family: str
    package_version: str
    data_version: str
    feature_set: str
    training_date: str | None = None
    metrics: Metrics | None = None
    timestamp: str


# ── /features response ─────────────────────────────────────────────────────────

class FieldDescriptor(BaseModel):
    name: str
    position: int
    data_type: str
    required: bool
    minimum: float | None = None
    maximum: float | None = None
    allowed_categories: list[str] | None = None
    default_policy: str


class FeaturesResponse(BaseModel):
    canonical_fields: list[FieldDescriptor]
    selected_features: list[str]
    total_input_fields: int
    total_selected_features: int
