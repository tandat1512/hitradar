"""Test SHAP page: no direct SHAP, causal wording, API payload — Feature 3.3 Phase 4"""
import pytest
import os


def test_shap_page_no_shap_import():
    """SHAP page must not import shap, shap.TreeExplainer, or any shap module."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["import shap", "shap.TreeExplainer", "shap.Explainer",
                 "shap_values", ".npy", ".joblib"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 2_Explain.py"


def test_shap_page_no_shap_artifact_read():
    """SHAP page must not read SHAP artifacts directly."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["open(", "np.load", "joblib.load"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 2_Explain.py"


def test_shap_page_calls_api_explain():
    """SHAP page must call client.explain() (POST /explain)."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    assert "client.explain" in content, "Page must call client.explain()"


def test_shap_page_no_direct_model_access():
    """SHAP page must not import backend services or model libs."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["ModelService", "ExplainService", "WhatIfService",
                "from app.", "joblib", "xgboost"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 2_Explain.py"


def test_shap_page_no_causal_claim():
    """SHAP page must not claim causation."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    causal_phrases = [
        " causes ", " cause ", "causes popularity",
        " will increase ", " will decrease ",
        " real effect", " actual effect",
    ]
    # Lower-case check
    lower = content.lower()
    for phrase in causal_phrases:
        assert phrase not in lower, f"Causal phrase '{phrase}' must not appear in 2_Explain.py"


def test_shap_page_has_model_behavior_caption():
    """SHAP page must show 'model behavior' attribution."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "model behavior" in lower, \
        "SHAP page must contain 'model behavior' attribution caption"


def test_shap_page_has_causal_disclaimer():
    """SHAP page must have causal disclaimer."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert ("causal" in lower or "cause" in lower), \
        "SHAP page must contain causal disclaimer"


def test_shap_page_uses_session_input():
    """SHAP page must reuse cached prediction input from session state."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    assert "current_prediction_input" in content, \
        "Page must read from current_prediction_input session state"


def test_shap_page_saves_explanation_session():
    """SHAP page must save explanation to session state."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "2_Explain.py")
    content = open(path, encoding="utf-8").read()
    assert "current_explanation" in content, \
        "Page must save to current_explanation session state"


def test_shap_component_renders_empty_state():
    """Empty state function must be callable."""
    from components.shap_explanation import render_shap_empty_state
    assert callable(render_shap_empty_state)
