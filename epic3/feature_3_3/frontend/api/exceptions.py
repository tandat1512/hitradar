"""
API Exception Hierarchy — Feature 3.3.

Maps HTTP errors and network failures to typed exceptions.

Error format: Backend (Feature 3.2) uses ErrorResponse:
  {"error": {"code": "...", "message": "...", "details": [...]},
   "request_id": "...", "timestamp": "..."}

FastAPI/HTTPException may return:
  {"detail": "message"}   — FastAPI default for 400/404/500
  {"detail": [...]}        — FastAPI validation for 422

The parser handles both formats.
"""
from __future__ import annotations


class APIClientError(Exception):
    """Base exception for all API client errors."""

    def __init__(self, message: str, request_id: str | None = None):
        super().__init__(message)
        self.request_id = request_id


class APIConnectionError(APIClientError):
    """Network-level error: DNS failure, connection refused, etc."""


class APITimeoutError(APIClientError):
    """Request timed out (connect or read)."""


class APIResponseError(APIClientError):
    """HTTP response received but status code indicates error."""

    def __init__(
        self,
        message: str,
        status_code: int,
        request_id: str | None = None,
    ):
        super().__init__(message, request_id)
        self.status_code = status_code


class APIValidationError(APIResponseError):
    """HTTP 422 — request validation failed."""

    def __init__(
        self,
        message: str,
        status_code: int = 422,
        request_id: str | None = None,
        field_errors: list[dict] | None = None,
    ):
        super().__init__(message, status_code, request_id)
        self.field_errors = field_errors or []


class APIServiceUnavailableError(APIResponseError):
    """HTTP 503 — backend or model unavailable."""


class APIContractError(APIClientError):
    """Response JSON parsed but schema doesn't match expected contract."""


def parse_backend_error(status_code: int, response_body: bytes) -> APIClientError:
    """
    Parse a raw error response body into a typed API exception.

    Handles two formats:
    1. Feature 3.2 ErrorResponse:
         {"error": {"code": "...", "message": "...", "details": [...]},
          "request_id": "...", "timestamp": "..."}
    2. FastAPI HTTPException:
         {"detail": "message"}   — for 400/404/500
         {"detail": [...]}       — for 422 validation
    """
    import json

    try:
        body = json.loads(response_body)
    except Exception:
        return APIResponseError(
            f"HTTP {status_code} — malformed error response",
            status_code=status_code,
        )

    # ── Format 1: Feature 3.2 ErrorResponse ────────────────────────────────
    error_obj = body.get("error", {})
    if isinstance(error_obj, dict):
        error_message = error_obj.get("message", "")
        error_details = error_obj.get("details", [])

        if status_code == 422 and error_details:
            field_errors = [
                {
                    "field": ".".join(str(p) for p in e.get("field", "").split(".")),
                    "issue": e.get("issue", e.get("msg", "")),
                    "code": e.get("code", ""),
                }
                for e in error_details
                if isinstance(e, dict)
            ]
            return APIValidationError(
                message=error_message or "Request validation failed",
                status_code=422,
                field_errors=field_errors,
            )

        if status_code == 503:
            return APIServiceUnavailableError(
                error_message or "Service temporarily unavailable",
                status_code=status_code,
            )

        return APIResponseError(
            error_message or f"HTTP {status_code}",
            status_code=status_code,
        )

    # ── Format 2: FastAPI HTTPException {"detail": ...} ─────────────────────
    detail = body.get("detail", "")

    if status_code == 422:
        field_errors = []
        if isinstance(detail, list):
            field_errors = [
                {
                    "field": ".".join(str(p) for p in e.get("loc", [])),
                    "issue": e.get("msg", ""),
                    "code": e.get("type", ""),
                }
                for e in detail
            ]
        return APIValidationError(
            message="Request validation failed",
            status_code=422,
            field_errors=field_errors,
        )

    if status_code == 503:
        msg = detail if isinstance(detail, str) else "Service temporarily unavailable"
        return APIServiceUnavailableError(msg, status_code=status_code)

    msg = detail if isinstance(detail, str) else f"HTTP {status_code}"
    return APIResponseError(msg, status_code=status_code)
