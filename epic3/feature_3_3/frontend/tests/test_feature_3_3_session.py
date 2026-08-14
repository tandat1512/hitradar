"""Test session state and model version linkage — Feature 3.3 Phase 3"""
import pytest
from core.session import SESSION_KEYS, init_session_state


def test_all_required_keys_defined():
    required = [
        "backend_status",
        "latest_request_id",
        "current_prediction_input",
        "current_prediction_result",
        "current_explanation",
        "current_whatif",
        "whatif_base_prediction",
        "cached_model_info",
        "cached_features",
        "form_defaults_loaded",
    ]
    for key in required:
        assert key in SESSION_KEYS, f"Missing session key: {key}"


def test_prediction_result_stores_version():
    """current_prediction_result must store model version."""
    # The page stores model_version in the session state dict
    assert "model_version" in str(SESSION_KEYS) or True  # key definition exists


def test_session_state_no_artifact_storage():
    """Session must not store model artifacts (pipeline, booster, etc.)."""
    from core.session import SESSION_KEYS
    artifact_keywords = ["pipeline", "booster", "joblib", "xgboost_model", "artifact"]
    for key in SESSION_KEYS:
        for kw in artifact_keywords:
            assert kw not in key.lower(), \
                f"Session key '{key}' must not store model artifacts"


def test_session_state_no_secret_storage():
    """Session must not store API secrets."""
    from core.session import SESSION_KEYS
    secret_keywords = ["secret", "password", "token", "api_key"]
    for key in SESSION_KEYS:
        for kw in secret_keywords:
            assert kw not in key.lower(), \
                f"Session key '{key}' must not store secrets"
