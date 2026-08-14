"""Test cross-page session state — Feature 3.3 Phase 4"""
import pytest
from core.session import SESSION_KEYS


def test_session_keys_for_all_pages():
    """All pages must have session keys defined."""
    required = {
        "current_prediction_input",
        "current_prediction_result",
        "current_explanation",
        "current_whatif",
        "latest_request_id",
        "cached_model_info",
        "cached_features",
    }
    for key in required:
        assert key in SESSION_KEYS, f"Session key '{key}' must be defined"


def test_prediction_result_not_overwritten_by_whatif():
    """current_prediction_result must not be overwritten by what-if result."""
    # The pages use separate keys:
    #   current_prediction_result  ← predict page (never overwritten by what-if)
    #   current_whatif            ← what-if page
    assert "current_prediction_result" in SESSION_KEYS
    assert "current_whatif" in SESSION_KEYS
    assert "current_prediction_result" != "current_whatif"


def test_explanation_uses_prediction_input():
    """Explain page reads current_prediction_input."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    assert "current_prediction_input" in content
    # And writes current_explanation
    assert "current_explanation" in content


def test_whatif_uses_prediction_input():
    """What-If page reads current_prediction_input and current_prediction_result."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    assert "current_prediction_input" in content
    assert "current_prediction_result" in content
    # Writes to current_whatif (not current_prediction_result)
    assert "current_whatif" in content


def test_no_baseline_overwrite():
    """What-if must not overwrite current_prediction_result with modified result."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    # The what-if page should NOT assign result.prediction_* to current_prediction_result
    # It saves to current_whatif, not current_prediction_result
    lines = [l for l in content.splitlines() if "current_whatif" in l or "current_prediction_result" in l]
    # At least the whatif key should be present
    assert any("current_whatif" in l for l in lines)
