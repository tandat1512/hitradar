"""
HitRadar API Client — Feature 3.3.

HTTP client that calls FastAPI backend via REST API.
No Streamlit calls here — purely HTTP + typed responses.
"""
from __future__ import annotations

import uuid
from typing import Any

import httpx

from api.exceptions import (
    APIClientError,
    APIConnectionError,
    APIContractError,
    APIServiceUnavailableError,
    APITimeoutError,
    APIValidationError,
    parse_backend_error,
)
from api.models import (
    ExplainResponse,
    FeaturesResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictResponse,
    WhatIfResponse,
)


# ── Endpoint Registry ─────────────────────────────────────────────────────────

ENDPOINTS = {
    "health":     {"method": "GET",  "path": "/health"},
    "model_info": {"method": "GET",  "path": "/model-info"},
    "features":   {"method": "GET",  "path": "/features"},
    "predict":    {"method": "POST", "path": "/predict"},
    "explain":    {"method": "POST", "path": "/explain"},
    "what_if":    {"method": "POST", "path": "/what-if"},
}


def _build_url(base_url: str, api_prefix: str, path: str) -> str:
    """Build a clean URL, handling prefixes and trailing slashes safely."""
    base = base_url.rstrip("/")
    prefix = f"/{api_prefix.strip('/')}" if api_prefix else ""
    return f"{base}{prefix}{path}"


def _new_request_id() -> str:
    """Generate a new client-side request ID."""
    return str(uuid.uuid4())


# ── HTTP Client ──────────────────────────────────────────────────────────────

class HitRadarAPIClient:
    """
    HTTP API client for HitRadar Pro FastAPI backend.

    All methods return typed response objects or raise typed exceptions.
    No Streamlit calls — reusable outside the UI layer.
    """

    def __init__(
        self,
        base_url: str,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        request_timeout: float = 35.0,
        api_prefix: str = "",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=10.0,
                pool=5.0,
            ),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    # ── HTTP verb wrappers ──────────────────────────────────────────────────

    def _get(self, path: str, request_id: str) -> dict:
        url = _build_url(self.base_url, self.api_prefix, path)
        headers = {"X-Request-ID": request_id}
        try:
            response = self._client.get(url, headers=headers)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timed out: {e}") from e
        return self._handle_response(response, request_id)

    def _post(self, path: str, payload: dict, request_id: str) -> dict:
        url = _build_url(self.base_url, self.api_prefix, path)
        headers = {"X-Request-ID": request_id}
        try:
            response = self._client.post(url, json=payload, headers=headers)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {e}") from e
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timed out: {e}") from e
        return self._handle_response(response, request_id)

    def _handle_response(self, response: httpx.Response, request_id: str) -> dict:
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                raise APIContractError(f"Failed to parse JSON: {e}", request_id=request_id)
        else:
            exc = parse_backend_error(response.status_code, response.content)
            exc.request_id = request_id
            raise exc

    # ── Typed API methods ──────────────────────────────────────────────────

    def health(self) -> HealthResponse:
        """Call GET /health — returns structured health response."""
        request_id = _new_request_id()
        data = self._get(ENDPOINTS["health"]["path"], request_id)
        return HealthResponse(data)

    def get_model_info(self) -> ModelInfoResponse:
        """Call GET /model-info — returns model metadata."""
        request_id = _new_request_id()
        data = self._get(ENDPOINTS["model_info"]["path"], request_id)
        return ModelInfoResponse(data)

    def get_features(self) -> FeaturesResponse:
        """Call GET /features — returns canonical fields and selected features."""
        request_id = _new_request_id()
        data = self._get(ENDPOINTS["features"]["path"], request_id)
        return FeaturesResponse(data)

    def predict(self, payload: dict) -> PredictResponse:
        """Call POST /predict — returns popularity prediction."""
        request_id = _new_request_id()
        data = self._post(ENDPOINTS["predict"]["path"], payload, request_id)
        result = PredictResponse(data)
        if not result.is_valid():
            raise APIContractError(
                f"Invalid prediction response: prediction_raw={result.prediction_raw}",
                request_id=request_id,
            )
        return result

    def explain(self, payload: dict) -> ExplainResponse:
        """Call POST /explain — returns SHAP explanation."""
        request_id = _new_request_id()
        data = self._post(ENDPOINTS["explain"]["path"], payload, request_id)
        result = ExplainResponse(data)
        if not result.is_valid():
            raise APIContractError(
                f"Invalid explain response: prediction={result.prediction}",
                request_id=request_id,
            )
        return result

    def what_if(self, base_features: dict, changed_features: dict) -> WhatIfResponse:
        """
        Call POST /what-if — returns scenario comparison.

        Args:
            base_features: 18-field PredictRequest dict.
            changed_features: dict of fields to change.
        """
        request_id = _new_request_id()
        data = self._post(
            ENDPOINTS["what_if"]["path"],
            {"base_features": base_features, "changed_features": changed_features},
            request_id,
        )
        result = WhatIfResponse(data)
        if not result.is_valid():
            raise APIContractError(
                f"Invalid what-if response: before={result.prediction_before} after={result.prediction_after}",
                request_id=request_id,
            )
        return result
