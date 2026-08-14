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


class ClusterInput(BaseModel):
    """Only audio fields actually used by the saved KMeans pipeline."""

    model_config = ConfigDict(extra="forbid")

    duration_min: float = Field(ge=0.1, le=60.0)
    danceability: float = Field(ge=0.0, le=1.0)
    energy: float = Field(ge=0.0, le=1.0)
    loudness: float = Field(ge=-80.0, le=10.0)
    speechiness: float = Field(ge=0.0, le=1.0)
    acousticness: float = Field(ge=0.0, le=1.0)
    instrumentalness: float = Field(ge=0.0, le=1.0)
    liveness: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=0.0, le=1.0)
    tempo: float = Field(gt=0.0, le=300.0)


class PredictionResponse(BaseModel):
    predicted_popularity: float
    popularity_tier: str
    model_name: str
    engineered_feature_count: int
    feature_count: int
    prediction_support_status: Literal[
        "within_product_support", "temporal_extrapolation"
    ]
    temporal_extrapolation: bool
    support_note: str
    train_end_year: int
    product_support_end_year: int
    observed_data_max_year: int
    final_holdout_max_year: int


class ClusterResponse(BaseModel):
    cluster: int
    chosen_k: int
    feature_count: int


class RecommendationItem(BaseModel):
    track_id: str
    cosine_similarity: float


class RecommendationResponse(BaseModel):
    query_track_id: str
    recommendations: list[RecommendationItem]
    feature_count: int
    metadata_note: str
