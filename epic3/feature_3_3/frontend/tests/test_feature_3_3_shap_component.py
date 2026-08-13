"""Test SHAP explanation component — Feature 3.3 Phase 2"""
import pytest
from api.models import ExplainResponse


def make_explain_response(**overrides):
    defaults = dict(
        prediction=65.43,
        base_value=29.56,
        contributions=[
            {"feature": "release_year", "value": 2020, "contribution": 15.2, "type": "positive"},
            {"feature": "acousticness", "value": 0.2, "contribution": -2.3, "type": "negative"},
            {"feature": "danceability", "value": 0.7, "contribution": 3.1, "type": "positive"},
        ],
        request_id="test-uuid-5678",
    )
    defaults.update(overrides)
    return ExplainResponse(defaults)


# ── Direction correctness ───────────────────────────────────────────────

def test_shap_positive_contribution_sign():
    """Positive contribution must have positive sign."""
    result = make_explain_response()
    for c in result.contributions:
        if c["contribution"] > 0:
            assert c["type"] == "positive"


def test_shap_negative_contribution_sign():
    """Negative contribution must have negative sign."""
    result = make_explain_response()
    for c in result.contributions:
        if c["contribution"] < 0:
            assert c["type"] == "negative"


def test_shap_no_causal_language_in_response():
    """Backend response must not claim causation."""
    result = make_explain_response()
    import json
    raw = json.dumps({"prediction": result.prediction, "contributions": result.contributions})
    # No causal language in response payload
    assert "cause" not in raw.lower()
    assert "effect" not in raw.lower()


def test_shap_is_valid_finite():
    """Prediction must be finite."""
    result = make_explain_response()
    assert result.is_valid()


def test_shap_contributions_sortable():
    """Contributions must be sortable by value."""
    result = make_explain_response()
    contribs = [(c["feature"], c["contribution"]) for c in result.contributions]
    sorted_desc = sorted(contribs, key=lambda x: x[1], reverse=True)
    assert sorted_desc[0][0] == "release_year"  # 15.2 is highest


def test_shap_empty_contributions():
    """Component must handle empty contributions gracefully."""
    result = make_explain_response(contributions=[])
    assert result.contributions == []


def test_shap_base_value_accessible():
    """Base value from backend should be accessible."""
    result = make_explain_response(base_value=30.0)
    assert result.base_value == 30.0
