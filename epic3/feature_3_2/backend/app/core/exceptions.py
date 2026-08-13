"""
Custom exceptions and error codes — Feature 3.2 FastAPI Backend.
"""
from __future__ import annotations


class BackendError(Exception):
    """Base exception for all backend errors."""

    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    message: str = "An internal error occurred."

    def __init__(self, message: str | None = None, details: dict | None = None):
        self.message = message or self.__class__.message
        self.details = details or {}
        super().__init__(self.message)


# ── Model errors ───────────────────────────────────────────────────────────────

class ModelNotLoadedError(BackendError):
    """Model pipeline is not yet loaded."""
    code = "MODEL_NOT_LOADED"
    status_code = 503
    message = "Model not loaded — service degraded."


class ModelLoadError(BackendError):
    """Pipeline failed to deserialize."""
    code = "MODEL_LOAD_FAILED"
    status_code = 500
    message = "Failed to load model pipeline."


class ModelPredictionError(BackendError):
    """Prediction step failed at runtime."""
    code = "PREDICTION_FAILED"
    status_code = 422
    message = "Prediction computation failed."


class SchemaNotFoundError(BackendError):
    """Required schema artifact not found."""
    code = "SCHEMA_NOT_FOUND"
    status_code = 500
    message = "Required schema artifact is missing."


# ── Validation errors ──────────────────────────────────────────────────────────

class InvalidFeatureError(BackendError):
    """Feature name in what-if is not in canonical list."""
    code = "INVALID_FEATURE"
    status_code = 422
    message = "Feature is not a valid canonical input field."


class TargetFieldError(BackendError):
    """target_popularity or track_id appeared as input feature."""
    code = "TARGET_FIELD_REJECTED"
    status_code = 422
    message = "target_popularity must not be included as an input feature."


# ── Explanation errors ─────────────────────────────────────────────────────────

class ExplanationError(BackendError):
    """SHAP explanation computation failed."""
    code = "EXPLANATION_FAILED"
    status_code = 500
    message = "Feature explanation computation failed."


# ── Config errors ─────────────────────────────────────────────────────────────

class ArtifactPathError(BackendError):
    """Artifact path is invalid or points outside allowed directory."""
    code = "ARTIFACT_PATH_INVALID"
    status_code = 500
    message = "Artifact path configuration is invalid."


class ArtifactNotFoundError(BackendError):
    """Required artifact file does not exist."""
    code = "ARTIFACT_NOT_FOUND"
    status_code = 500
    message = "Required artifact file was not found."
