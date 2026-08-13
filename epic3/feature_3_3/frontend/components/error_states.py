"""
Error, Warning & Status Components — Feature 3.3 Phase 2.

No network calls. No model loading.
"""
from __future__ import annotations

import streamlit as st

from api.exceptions import (
    APIClientError,
    APIConnectionError,
    APITimeoutError,
    APIValidationError,
    APIServiceUnavailableError,
    APIResponseError,
    APIContractError,
)


def render_error(error: Exception, request_id: str | None = None) -> None:
    """
    Render a user-friendly error from any API exception type.

    Never exposes: stack trace, absolute paths, Python repr, secrets.
    """
    rid = request_id or getattr(error, "request_id", None) or "N/A"

    if isinstance(error, APIValidationError):
        _render_validation_error(error, rid)
    elif isinstance(error, APIServiceUnavailableError):
        _render_service_unavailable(error, rid)
    elif isinstance(error, APITimeoutError):
        _render_timeout_error(error, rid)
    elif isinstance(error, APIConnectionError):
        _render_connection_error(error, rid)
    elif isinstance(error, APIResponseError):
        _render_http_error(error, rid)
    elif isinstance(error, APIContractError):
        _render_contract_error(error, rid)
    else:
        _render_generic_error(error, rid)


def _render_validation_error(error: APIValidationError, rid: str) -> None:
    st.error("Request validation failed")

    if error.field_errors:
        for fe in error.field_errors:
            field = fe.get("field", "unknown")
            issue = fe.get("issue", "invalid value")
            st.markdown(f"- **{field}**: {issue}")
    else:
        st.markdown(error.args[0] if error.args else "One or more fields are invalid.")

    st.caption(f"Request ID: `{rid}`")
    st.info("💡 Check that all values are within their allowed ranges.")


def _render_service_unavailable(error: Exception, rid: str) -> None:
    st.error("Service temporarily unavailable")
    st.markdown("The backend model is not ready. Please try again in a moment.")
    st.caption(f"Request ID: `{rid}`")
    st.info("💡 If the problem persists, check that the backend server is running.")


def _render_timeout_error(error: Exception, rid: str) -> None:
    st.error("Request timed out")
    st.markdown("The backend took too long to respond.")
    st.caption(f"Request ID: `{rid}`")
    st.info("💡 Try again. If it persists, the backend may be overloaded.")


def _render_connection_error(error: Exception, rid: str) -> None:
    st.error("Cannot connect to backend")
    st.markdown(
        "The frontend could not reach the backend server. "
        "Verify that the backend is running and `BACKEND_BASE_URL` is configured correctly."
    )
    st.caption(f"Request ID: `{rid}`")
    st.info("💡 Check that the FastAPI backend is running on the configured host and port.")


def _render_http_error(error: APIResponseError, rid: str) -> None:
    st.error(f"Backend error ({error.status_code})")
    st.markdown(error.args[0] if error.args else f"HTTP {error.status_code}")
    st.caption(f"Request ID: `{rid}`")


def _render_contract_error(error: Exception, rid: str) -> None:
    st.error("Unexpected response from backend")
    st.markdown("The backend returned data in an unexpected format.")
    st.caption(f"Request ID: `{rid}`")
    st.info("💡 Please report this — the API contract may need review.")


def _render_generic_error(error: Exception, rid: str) -> None:
    st.error("Something went wrong")
    st.markdown("An unexpected error occurred. Please try again.")
    st.caption(f"Request ID: `{rid}`")


# ── Warning ──────────────────────────────────────────────────────────────────

def render_warning(message: str) -> None:
    """Render a non-blocking warning message."""
    st.warning(f"⚠️ {message}")


def render_backend_degraded_warning() -> None:
    st.warning(
        "⚠️ Backend is in degraded mode. "
        "Predictions may be unavailable. Try refreshing."
    )


def render_provisional_result_warning() -> None:
    st.warning(
        "⚠️ Result based on the current model version. "
        "Metrics may change with model updates."
    )


# ── Loading ────────────────────────────────────────────────────────────────

def render_loading(message: str = "Processing...") -> None:
    """Render a spinner with a message. Use with `with`."""
    st.spinner(message)


def with_loading(message: str, func, *args, **kwargs):
    """
    Execute func inside a loading spinner.

    Usage:
        result = with_loading("Predicting...", client.predict, payload)
    """
    with st.spinner(message):
        return func(*args, **kwargs)


# ── Empty state helpers ────────────────────────────────────────────────────

def render_predict_empty_state() -> None:
    st.info(
        "📋 **Predict Song Popularity**  \n"
        "Enter song audio features in the form and click **Predict** "
        "to get a popularity score."
    )
    st.caption("Scores range from 0 to 100.")


def render_backend_unavailable_state() -> None:
    st.error("Backend unavailable")
    st.markdown(
        "The backend is not responding. Please ensure the FastAPI server "
        "is running and try refreshing the page."
    )
    st.info("💡 To start the backend: `uvicorn app.main:app --reload`")
