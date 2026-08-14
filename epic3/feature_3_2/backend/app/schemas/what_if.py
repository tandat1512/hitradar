"""
What-if schemas — Feature 3.2 FastAPI Backend.

Contract: send base input + changed features dict (not: send full modified input).
Changed features are merged into base at service layer.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.prediction import PredictRequest


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Request ─────────────────────────────────────────────────────────────────────

class WhatIfRequest(BaseModel):
    """
    What-if comparison request.

    Design choice (API-level): send base input + changed_features dict.
    Rationale: caller only needs to specify what changes, not the full record.

    Validation rules:
    - Every key in changed_features must be in CANONICAL_FIELD_NAMES
    - target_popularity is rejected at PredictRequest level
    - Empty changed_features is rejected (min_length=1)
    - Unknown field names raise 422
    """
    base_features: PredictRequest
    changed_features: dict[str, float | bool | int | str] = Field(
        ...,
        min_length=1,
        description="Feature overrides to apply on top of base_features",
    )

    model_config = {"extra": "forbid"}

    def validated_changed_keys(self) -> list[str]:
        """Return changed keys that are valid canonical field names."""
        return [
            k for k in self.changed_features
            if k in PredictRequest.CANONICAL_FIELD_NAMES
        ]

    def invalid_changed_keys(self) -> list[str]:
        """Return changed keys that are NOT in canonical field names."""
        return [
            k for k in self.changed_features
            if k not in PredictRequest.CANONICAL_FIELD_NAMES
        ]


# ── Response ────────────────────────────────────────────────────────────────────

class PredictionShort(BaseModel):
    """Abbreviated prediction result used in what-if comparison."""
    prediction_raw: float
    prediction_clipped: float
    prediction_display: int

    model_config = {"extra": "forbid"}


class WhatIfResponse(BaseModel):
    """
    Side-by-side prediction comparison.

    delta = prediction_after - prediction_before
    A positive delta means the changes increase the predicted popularity score.
    """
    status: str
    prediction_before: PredictionShort
    prediction_after: PredictionShort
    delta: float = Field(
        description="prediction_after - prediction_before (clipped values)"
    )
    delta_display: int = Field(
        description="delta rounded to integer for display"
    )
    changes_applied: dict[str, float | bool | int | str] = Field(
        description="The exact changes that were applied"
    )
    model_id: str
    model_version: str
    request_id: str | None = Field(default=None)
    timestamp: str = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}
