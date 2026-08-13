"""
Prediction schemas — Feature 3.2 FastAPI Backend.

Request contract: 18 canonical input fields from input_schema.json.
Response contract: output_schema.json + API-level metadata (request_id, timestamp).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Request ─────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """
    Canonical 18-field input for track popularity prediction.

    Field names and constraints sourced from:
    - input_schema.json (HITRADAR-PREDICTION-INPUT-V1)

    Target field (target_popularity) and identifier (track_id) are excluded.
    """
    duration_min: float = Field(..., ge=0.0, le=120.0, description="Track duration in minutes")
    explicit: bool = Field(..., description="Whether the track has explicit lyrics")
    release_year: int = Field(..., ge=1900, le=2100, description="Release year")
    release_month: float = Field(..., ge=1.0, le=12.0, description="Release month (1–12)")
    decade: int = Field(..., ge=1900, le=2100, description="Decade bucket")
    release_precision: str = Field(
        ..., pattern=r"^(day|month|year)$",
        description="Precision of the release date"
    )
    danceability: float = Field(..., ge=0.0, le=1.0, description="Danceability score")
    energy: float = Field(..., ge=0.0, le=1.0, description="Energy score")
    key: int = Field(..., ge=0, le=11, description="Musical key (0–11)")
    loudness: float = Field(..., ge=-60.0, le=0.0, description="Loudness in dB")
    mode: int = Field(..., ge=0, le=1, description="Mode (0=minor, 1=major)")
    speechiness: float = Field(..., ge=0.0, le=1.0, description="Speechiness score")
    acousticness: float = Field(..., ge=0.0, le=1.0, description="Acousticness score")
    instrumentalness: float = Field(..., ge=0.0, le=1.0, description="Instrumentalness score")
    liveness: float = Field(..., ge=0.0, le=1.0, description="Liveness score")
    valence: float = Field(..., ge=0.0, le=1.0, description="Valence score")
    tempo: float = Field(..., ge=0.0, le=300.0, description="Tempo in BPM")
    time_signature: float = Field(..., description="Time signature")

    # Canonical 18 field names — used by /what-if to validate changed_features
    CANONICAL_FIELD_NAMES: frozenset[str] = frozenset({
        "duration_min", "explicit", "release_year", "release_month", "decade",
        "release_precision", "danceability", "energy", "key", "loudness",
        "mode", "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo", "time_signature",
    })

    model_config = {
        "extra": "allow",
        "json_schema_extra": {
            "example": {
                "duration_min": 3.517,
                "explicit": False,
                "release_year": 1992,
                "release_month": 1.0,
                "decade": 1990,
                "release_precision": "year",
                "danceability": 0.7,
                "energy": 0.8,
                "key": 5,
                "loudness": -5.0,
                "mode": 1,
                "speechiness": 0.1,
                "acousticness": 0.3,
                "instrumentalness": 0.05,
                "liveness": 0.2,
                "valence": 0.6,
                "tempo": 120.0,
                "time_signature": 4.0,
            }
        },
    }


# ── Response ────────────────────────────────────────────────────────────────────

class PredictResponse(BaseModel):
    """
    Prediction result response.

    Fields from output_schema.json (HITRADAR-PREDICTION-OUTPUT-V1):
    - status, model_id, model_version, package_version
    - prediction_raw, prediction_clipped, prediction_display, warnings

    API-level fields:
    - request_id (optional, set by router)
    - timestamp
    """
    status: str = Field(description="'SUCCESS' or 'ERROR'")
    prediction_raw: float = Field(
        description="Raw model output — may be outside [0, 100]"
    )
    prediction_clipped: float = Field(
        description="Clipped to [0, 100]"
    )
    prediction_display: int = Field(
        description="Rounded clipped value for display"
    )
    model_id: str = Field(description="Champion model ID")
    model_version: str = Field(description="Model version")
    package_version: str = Field(description="Package version")
    warnings: list[str] = Field(default_factory=list)
    request_id: str | None = Field(default=None, description="API-level request trace ID")
    timestamp: str = Field(default_factory=_utc_now)

    model_config = {"extra": "forbid"}
