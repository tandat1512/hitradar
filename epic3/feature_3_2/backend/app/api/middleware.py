"""
Request ID + structured logging middleware — Feature 3.2 Phase 3.

- X-Request-ID: accept from client, else generate UUID4.
- Structured JSON request/response log per request.
- Sensitive header redaction.
- Latency tracking.
"""
from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── Redaction list ──────────────────────────────────────────────────────────────
SENSITIVE_HEADERS = frozenset({
    "authorization", "proxy-authorization", "cookie", "set-cookie",
    "x-api-key", "x-auth-token", "x-csrf-token",
})
REDACTED = "[REDACTED]"
MAX_REQUEST_ID_LEN = 64


def _redact_header(key: str, value: str) -> str:
    return REDACTED if key.lower() in SENSITIVE_HEADERS else value


def _normalize_request_id(raw: str | None) -> str:
    """Accept only safe UUID-formatted strings, otherwise generate."""
    if raw and len(raw) <= MAX_REQUEST_ID_LEN:
        # allow only alphanumeric, dash, underscore (basic safety)
        if re.match(r"^[a-zA-Z0-9_-]+$", raw):
            return raw[:MAX_REQUEST_ID_LEN]
    return str(uuid.uuid4())


# ── JSON log helper ───────────────────────────────────────────────────────────
def _json_log(**fields) -> str:
    """Serialize one log line as a compact single-line JSON string."""
    import json
    return json.dumps(fields, separators=(",", ":"))


# ── Middleware ──────────────────────────────────────────────────────────────────
_request_logger = logging.getLogger("app.middleware.request")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject X-Request-ID into request state and response headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        raw_id = request.headers.get("x-request-id")
        request_id = _normalize_request_id(raw_id)
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, route, status, duration, request_id for every request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = getattr(request.state, "request_id", "-")
        started_at = time.perf_counter()
        method = request.method
        path = request.url.path

        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        status = response.status_code

        # Redact sensitive query params
        redacted_query = {}
        for k, v in dict(request.query_params).items():
            redacted_query[k] = REDACTED if k.lower() in SENSITIVE_HEADERS else v

        _request_logger.info(_json_log(
            event="request",
            request_id=request_id,
            method=method,
            path=path,
            status=status,
            duration_ms=duration_ms,
            client=request.client.host if request.client else "-",
            user_agent=request.headers.get("user-agent", "-"),
            redacted_query=redacted_query,
        ))

        return response
