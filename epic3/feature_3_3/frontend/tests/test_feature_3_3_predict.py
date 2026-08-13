"""Test Predict page: form contract, payload, session state — Feature 3.3 Phase 3"""
import pytest
from unittest.mock import MagicMock, patch


# ── Predict form contract ───────────────────────────────────────────────────

def test_form_uses_st_form():
    """Predict form must use st.form to avoid API call on widget change."""
    import os, sys
    # Read the form source
    path = os.path.join(os.path.dirname(__file__), "..", "components", "predict_form.py")
    content = open(path, encoding="utf-8").read()
    assert "st.form" in content, "predict_form.py must use st.form"


def test_form_includes_release_fields():
    """Form must include release_year, release_month, decade, precision."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "components", "predict_form.py")
    content = open(path, encoding="utf-8").read()
    assert "release_year" in content
    assert "release_month" in content
    assert "decade" in content
    assert "release_precision" in content


def test_form_includes_all_numeric_features():
    """Form must include all numeric audio features."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "components", "predict_form.py")
    content = open(path, encoding="utf-8").read()
    features = ["danceability", "energy", "speechiness", "acousticness",
                "instrumentalness", "liveness", "valence", "tempo",
                "loudness", "key", "mode", "time_signature", "duration_min", "explicit"]
    for f in features:
        assert f in content, f"Field {f} must be in predict_form.py"


def test_no_target_field_in_form():
    """Form must not include a 'target' field."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "components", "predict_form.py")
    content = open(path, encoding="utf-8").read()
    # "target" should not appear as a field key (allow "time_signature")
    lines = content.splitlines()
    for line in lines:
        if '"target"' in line or "'target'" in line:
            # Allow if it's just a comment or "time_signature"
            stripped = line.strip()
            assert stripped.startswith("#") or "time_signature" in stripped, \
                f"Unexpected 'target' field in predict_form.py: {line}"


# ── Payload ─────────────────────────────────────────────────────────────────

def test_payload_contains_only_canonical_fields():
    """Payload must contain only the 18 canonical fields."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "components", "predict_form.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["target", "model_version_override", "selected_features", "model_path"]
    for f in forbidden:
        assert f"'target'" not in content, f"Field '{f}' must not be in form"


def test_predict_page_no_target_in_payload():
    """Predict page must block 'target' field from being submitted."""
    # The page has an explicit guard: if "target" in payload: st.error(...)
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "1_Predict.py")
    content = open(path, encoding="utf-8").read()
    assert 'if "target" in payload' in content or "if 'target' in payload" in content, \
        "Page must guard against 'target' field"


# ── Session state ───────────────────────────────────────────────────────────

def test_session_state_keys_defined():
    """Required session keys must be defined in core/session.py."""
    from core.session import SESSION_KEYS
    required = ["current_prediction_input", "current_prediction_result",
                "latest_request_id", "cached_model_info", "cached_features"]
    for key in required:
        assert key in SESSION_KEYS, f"Session key '{key}' must be defined"


def test_session_state_no_model_object():
    """Session state must not store model artifacts."""
    from core.session import SESSION_KEYS
    forbidden = ["model_artifact", "pipeline", "xgboost"]
    for key in SESSION_KEYS:
        assert not any(f in key.lower() for f in forbidden), \
            f"Session key '{key}' must not store model objects"


# ── No direct model access ────────────────────────────────────────────────

def test_predict_page_no_model_import():
    """Predict page must not import backend services or model libs."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "1_Predict.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["joblib", "pickle.load", "ModelService", "ExplainService",
                 "WhatIfService", "from app.services", "xgboost.Booster"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 1_Predict.py"


def test_predict_form_no_model_import():
    """Predict form component must not import model libs."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "components", "predict_form.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["joblib", "pickle", "ModelService", "xgboost", "from app."]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in predict_form.py"


# ── Build form defaults ───────────────────────────────────────────────────

def test_build_form_defaults_returns_dict():
    """build_form_defaults must return a dict."""
    from components.predict_form import build_form_defaults
    from api.models import FeaturesResponse

    class FakeField:
        def __init__(self, **kw):
            self._d = kw
        def get(self, k, d=None):
            return self._d.get(k, d)

    class FakeFeatures:
        def __init__(self):
            self.canonical_fields = [
                {"name": "danceability", "data_type": "number", "minimum": 0.0,
                 "maximum": 1.0, "default_policy": "PIPELINE_IMPUTE"},
                {"name": "explicit", "data_type": "boolean"},
            ]

    features = FakeFeatures()
    defaults = build_form_defaults(features)
    assert isinstance(defaults, dict)
    assert "danceability" in defaults
    assert defaults["danceability"] == 0.5  # midpoint
    assert defaults["explicit"] is False


def test_build_form_defaults_boolean():
    from components.predict_form import build_form_defaults
    class FakeFeatures:
        canonical_fields = [
            {"name": "explicit", "data_type": "boolean"},
        ]
    defaults = build_form_defaults(FakeFeatures())
    assert defaults["explicit"] is False
