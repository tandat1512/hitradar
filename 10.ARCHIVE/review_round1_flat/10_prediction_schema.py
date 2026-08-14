"""Prediction schemas for raw Spotify track input."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TrackInput(BaseModel):
    """Only raw/cleaned inputs are accepted; engineered fields are forbidden."""

    model_config = ConfigDict(extra="forbid")

    duration_min: float = Field(ge=0.1, le=60.0)
    explicit: bool
    release_year: int = Field(ge=1900, le=2100)
    release_month: float | None = Field(default=None, ge=1, le=12)
    release_precision: Literal["day", "month", "year"]
    danceability: float = Field(ge=0.0, le=1.0)
    energy: float = Field(ge=0.0, le=1.0)
    key: int = Field(ge=0, le=11)
    loudness: float = Field(ge=-80.0, le=10.0)
    mode: int = Field(ge=0, le=1)
    speechiness: float = Field(ge=0.0, le=1.0)
    acousticness: float = Field(ge=0.0, le=1.0)
    instrumentalness: float = Field(ge=0.0, le=1.0)
    liveness: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=0.0, le=1.0)
    tempo: float = Field(gt=0.0, le=300.0)
    time_signature: float = Field(ge=1.0, le=7.0)


class PredictionResponse(BaseModel):
    predicted_popularity: float
    popularity_tier: str
    model_name: str
    engineered_feature_count: int
    feature_count: int
