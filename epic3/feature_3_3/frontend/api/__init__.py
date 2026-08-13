"""api package — Feature 3.3"""
from api.client import HitRadarAPIClient
from api.exceptions import (
    APIClientError,
    APIConnectionError,
    APIContractError,
    APIServiceUnavailableError,
    APITimeoutError,
    APIValidationError,
)
from api.models import (
    ExplainResponse,
    FeaturesResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictResponse,
    WhatIfResponse,
)

__all__ = [
    "HitRadarAPIClient",
    "APIClientError",
    "APIConnectionError",
    "APIContractError",
    "APIServiceUnavailableError",
    "APITimeoutError",
    "APIValidationError",
    "HealthResponse",
    "ModelInfoResponse",
    "FeaturesResponse",
    "PredictResponse",
    "ExplainResponse",
    "WhatIfResponse",
]
