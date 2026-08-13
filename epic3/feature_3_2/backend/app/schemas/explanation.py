"""
Explanation schemas — Feature 3.2 FastAPI Backend.

Source: input_schema.json (for request) + /explain contract from Feature 3.1 spec.
SHAP-based feature attribution. Correlations are not causal relationships.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Request ─────────────────────────────────────────────────────────────────────

class ExplainRequest(BaseModel):
    """
    Explain request uses the same 18-field input as PredictRequest.

    Optional controls (not yet in spec — reserved for future):
    - top_k: number of top features to return
    - include_all: return all 31 SHAP values
    """
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


# ── Response ────────────────────────────────────────────────────────────────────

class TopFeature(BaseModel):
    """A single feature with its SHAP contribution and raw value."""
    name: str = Field(description="Feature name from selected_features.json")
    shap_value: float = Field(
        description="SHAP contribution to the prediction (same unit as prediction)"
    )
    feature_value: float | str = Field(
        description="Raw input value for this feature"
    )

    model_config = {"extra": "forbid"}


class ExplainResponse(BaseModel):
    """
    Prediction result plus SHAP feature attribution.

    The shap_values map covers all 31 selected features.
    top_features lists the top 5 by absolute SHAP magnitude.

    IMPORTANT: SHAP values show feature importance, NOT causal relationships.
    """
    status: str
    prediction_raw: float
    prediction_clipped: float
    prediction_display: int
    base_value: float = Field(
        description="Expected (average) model output — shap.TreeExplainer.expected_value"
    )
    shap_values: dict[str, float] = Field(
        description="SHAP value per selected feature (31 entries)"
    )
    top_features: list[TopFeature] = Field(
        description="Top 5 features by absolute SHAP magnitude"
    )
    model_id: str
    model_version: str
    explanation_method: str = Field(
        default="SHAP_TreeExplainer",
        description="Explanation method identifier"
    )
    request_id: str | None = Field(default=None)
    timestamp: str = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}
