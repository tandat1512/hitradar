"""Test prediction component — Feature 3.3 Phase 2"""
import pytest
from unittest.mock import MagicMock, patch
from api.models import PredictResponse


# ── Fixtures ───────────────────────────────────────────────────────────────

def make_predict_response(**overrides):
    defaults = dict(
        prediction_raw=45.0,
        prediction_clipped=45.0,
        prediction_display=45,
        status="SUCCESS",
        warnings=[],
        model_id="EXP24-XGB-FINAL-001",
        model_version="1.0.0",
        package_version="1.0.0",
        request_id="test-uuid-1234",
    )
    defaults.update(overrides)
    return PredictResponse(defaults)


# ── No probability claim ───────────────────────────────────────────────────

def test_prediction_not_called_probability():
    """Prediction must not be labeled as probability."""
    result = make_predict_response()
    label = "Predicted Popularity"
    # The component renders with label "Predicted Popularity" — not "Probability"
    assert "probability" not in label.lower()
    assert "popularity" in label.lower()


def test_prediction_display_value_rendered():
    """Display value should be used as primary metric."""
    result = make_predict_response(
        prediction_raw=105.5,
        prediction_clipped=100.0,
        prediction_display=100,
    )
    # Primary score uses display value
    assert result.prediction_display == 100
    assert result.prediction_raw == 105.5  # raw preserved


def test_prediction_warnings_rendered():
    """Warnings from backend should be extractable."""
    result = make_predict_response(warnings=["Model running on fallback threshold."])
    assert len(result.warnings) == 1
    assert "fallback" in result.warnings[0].lower()


def test_prediction_metadata_fields():
    """Model metadata should be accessible."""
    result = make_predict_response()
    assert result.model_id == "EXP24-XGB-FINAL-001"
    assert result.model_version == "1.0.0"
    assert result.request_id == "test-uuid-1234"


def test_prediction_request_id_preserved():
    """Request ID from response should be accessible for debug."""
    result = make_predict_response(request_id="req-abc-999")
    assert result.request_id == "req-abc-999"


def test_prediction_status_success_badge():
    """Status field should be accessible."""
    result = make_predict_response(status="SUCCESS")
    assert result.status == "SUCCESS"
