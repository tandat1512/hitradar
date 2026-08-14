"""
API Response Models — Feature 3.3.

Lightweight response models for parsing backend API responses.
These are NOT Pydantic models — just plain dict accessors with validation.
"""
from __future__ import annotations


class HealthResponse:
    def __init__(self, data: dict):
        self.status: str = data.get("status", "unknown")
        self.model_loaded: bool = data.get("model_loaded", False)
        self.api_version: str = data.get("api_version", "unknown")
        self.request_id: str | None = data.get("request_id")

    def is_healthy(self) -> bool:
        return self.status == "healthy" and self.model_loaded

    def is_degraded(self) -> bool:
        return self.status == "degraded"


class ModelInfoResponse:
    def __init__(self, data: dict):
        self.model_id: str = data.get("model_id", "UNKNOWN")
        self.model_version: str = data.get("model_version", "unknown")
        self.model_family: str = data.get("model_family", "XGBoost")
        self.package_version: str = data.get("package_version", "unknown")
        self.data_version: str = data.get("data_version", "unknown")
        self.feature_set: str = data.get("feature_set", "")
        self.training_date: str | None = data.get("training_date")
        self.metrics = None
        raw_metrics = data.get("metrics")
        if raw_metrics and isinstance(raw_metrics, dict):
            self.metrics = _Metrics(raw_metrics)
        self.timestamp: str = data.get("timestamp", "")
        self.request_id: str | None = data.get("request_id")  # backward compat

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "model_family": self.model_family,
            "package_version": self.package_version,
            "data_version": self.data_version,
            "feature_set": self.feature_set,
            "training_date": self.training_date,
        }


class _Metrics:
    def __init__(self, data: dict):
        self.MAE: float | None = data.get("MAE")
        self.RMSE: float | None = data.get("RMSE")
        self.R2: float | None = data.get("R2")


class FeaturesResponse:
    def __init__(self, data: dict):
        self.canonical_fields: list[dict] = data.get("canonical_fields", [])
        self.selected_features: list[str] = data.get("selected_features", [])
        self.total_input_fields: int = data.get("total_input_fields", 0)
        self.total_selected_features: int = data.get("total_selected_features", 0)
        self.request_id: str | None = data.get("request_id")

    def get_field(self, name: str) -> dict | None:
        for f in self.canonical_fields:
            if f.get("name") == name:
                return f
        return None


class PredictResponse:
    def __init__(self, data: dict):
        self.prediction_raw: float = data.get("prediction_raw", 0.0)
        self.prediction_clipped: float = data.get("prediction_clipped", 0.0)
        self.prediction_display: int | str = data.get("prediction_display", 0)
        self.status: str = data.get("status", "unknown")
        self.warnings: list[str] = data.get("warnings", [])
        self.model_id: str = data.get("model_id", "")
        self.model_version: str = data.get("model_version", "")
        self.package_version: str = data.get("package_version", "")
        self.request_id: str | None = data.get("request_id")

    def is_valid(self) -> bool:
        import math
        return (
            isinstance(self.prediction_raw, (int, float))
            and math.isfinite(self.prediction_raw)
        )


class ExplainResponse:
    def __init__(self, data: dict):
        self.prediction: float = data.get("prediction", 0.0)
        self.base_value: float = data.get("base_value", 0.0)
        self.contributions: list[dict] = data.get("contributions", [])
        self.request_id: str | None = data.get("request_id")

    def is_valid(self) -> bool:
        import math
        return isinstance(self.prediction, (int, float)) and math.isfinite(self.prediction)


class WhatIfResponse:
    def __init__(self, data: dict):
        self.prediction_before: float = data.get("prediction_before", 0.0)
        self.prediction_after: float = data.get("prediction_after", 0.0)
        self.delta: float = data.get("delta", 0.0)
        self.changed_fields: list[str] = data.get("changed_fields", [])
        self.request_id: str | None = data.get("request_id")

    def is_valid(self) -> bool:
        import math
        return (
            isinstance(self.prediction_before, (int, float))
            and math.isfinite(self.prediction_before)
            and isinstance(self.prediction_after, (int, float))
            and math.isfinite(self.prediction_after)
        )
