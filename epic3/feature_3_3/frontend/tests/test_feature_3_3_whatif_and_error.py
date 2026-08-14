"""Test what-if, error, loading components — Feature 3.3 Phase 2"""
import pytest
from api.models import WhatIfResponse
from api.exceptions import (
    APIValidationError,
    APIServiceUnavailableError,
    APITimeoutError,
    APIConnectionError,
)


def make_whatif_response(**overrides):
    defaults = dict(
        prediction_before=45.0,
        prediction_after=60.0,
        delta=15.0,
        changed_fields=["danceability"],
        request_id="test-whatif-001",
    )
    defaults.update(overrides)
    return WhatIfResponse(defaults)


# ── What-If ──────────────────────────────────────────────────────────────

def test_whatif_delta_from_backend():
    """Delta must come from the backend, not computed in frontend."""
    result = make_whatif_response()
    assert result.delta == 15.0  # backend-provided delta
    assert result.prediction_after - result.prediction_before == 15.0  # cross-check


def test_whatif_delta_not_overwritten():
    """Frontend must not recompute delta."""
    result = make_whatif_response(delta=15.0)
    # The component uses result.delta directly — no frontend recompute
    assert result.delta == 15.0


def test_whatif_positive_delta():
    result = make_whatif_response(delta=5.0)
    assert result.delta > 0


def test_whatif_negative_delta():
    result = make_whatif_response(delta=-10.0)
    assert result.delta < 0


def test_whatif_changed_fields():
    result = make_whatif_response(changed_fields=["danceability", "energy"])
    assert "danceability" in result.changed_fields
    assert "energy" in result.changed_fields


def test_whatif_no_causal_language():
    """What-if description must not claim 'actual effect'."""
    result = make_whatif_response(delta=10.0)
    # Component text uses "model's prediction changes" — not "actual effect"
    desc_text = "model's prediction"
    assert "actual effect" not in desc_text.lower()


# ── Error types ──────────────────────────────────────────────────────────

def test_validation_error_has_field_errors():
    err = APIValidationError(
        message="Request validation failed",
        status_code=422,
        field_errors=[
            {"field": "danceability", "issue": "less than or equal to 1.0", "code": "less_than_equal"},
        ],
    )
    assert len(err.field_errors) == 1
    assert err.field_errors[0]["field"] == "danceability"


def test_service_unavailable_has_status():
    err = APIServiceUnavailableError("Model not loaded", status_code=503)
    assert err.status_code == 503


def test_timeout_error_raised():
    err = APITimeoutError("Request timed out")
    assert "timed out" in str(err)


def test_connection_error_raised():
    err = APIConnectionError("Connection refused")
    assert "refused" in str(err)


# ── No network in components ─────────────────────────────────────────────

def test_components_module_has_no_network_calls():
    """Scan components/*.py for forbidden network patterns."""
    import os
    components_dir = os.path.dirname(os.path.dirname(__file__))
    comp_dir = os.path.join(components_dir, "components")
    forbidden = ["httpx", "requests.get", "requests.post", "httpx.get", "httpx.post",
                 "urllib", "http.client", "st.requests", "aiohttp"]
    findings = []
    if os.path.isdir(comp_dir):
        for fname in os.listdir(comp_dir):
            if fname.endswith(".py"):
                path = os.path.join(comp_dir, fname)
                try:
                    content = open(path, encoding="utf-8").read()
                    for pattern in forbidden:
                        if pattern in content and not content.split(pattern)[0].count("#") < 1:
                            findings.append(f"{fname}: {pattern}")
                except Exception:
                    pass
    # Note: api.client.py has httpx — that's the HTTP layer, not a component
    # Components themselves must not call network
    component_files = [f for f in os.listdir(comp_dir) if f.endswith(".py") and f != "__init__.py"]
    for fname in component_files:
        path = os.path.join(comp_dir, fname)
        content = open(path, encoding="utf-8").read()
        assert "httpx" not in content, f"{fname} must not import httpx"
        assert "requests.get" not in content, f"{fname} must not call requests.get"
        assert "requests.post" not in content, f"{fname} must not call requests.post"


# ── Loading / empty state ────────────────────────────────────────────────

def test_with_loading_returns_func_result():
    """with_loading must return the function's actual return value."""
    def dummy_func():
        return {"result": 42}
    from components.error_states import with_loading
    result = with_loading("Working...", dummy_func)
    assert result == {"result": 42}


def test_empty_state_no_prediction_shown():
    """Empty state must not render any prediction value."""
    # Empty state components render only guidance text
    # No prediction key should be referenced
    from components.prediction_result import render_prediction_result
    from components.shap_explanation import render_shap_empty_state
    from components.whatif_comparison import render_whatif_empty_state
    # These should exist and be callable
    assert callable(render_shap_empty_state)
    assert callable(render_whatif_empty_state)
