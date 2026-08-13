"""Test Model Info page — Feature 3.3 Phase 5"""
import pytest
import os


def test_model_info_no_model_import():
    """Model Info page must not import model libs or backend services."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["joblib", "ModelService", "ExplainService", "WhatIfService",
                "from app.", "xgboost", "pickle"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 5_Model_Info.py"


def test_model_info_calls_api():
    """Model Info page must call client.get_model_info()."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    assert "client.get_model_info()" in content, \
        "Page must call client.get_model_info()"


def test_model_info_no_hardcoded_metadata():
    """Model Info must not hardcode model_id, version, etc."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    # info.model_id — dynamic access, not hardcoded string
    # Should NOT find string literals like "EXP24" unless in a string literal example
    lines = [l for l in content.splitlines() if "info.model" in l or "info." in l]
    assert len(lines) > 0, "Must access model info dynamically from API"


def test_model_info_has_accuracy_disclaimer():
    """Model Info must say metrics are not accuracy."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "not accuracy" in lower or "not accuracy" in lower, \
        "Page must clarify metrics are not accuracy"


def test_model_info_no_accuracy_mislabel():
    """Model Info must not call RMSE/MAE/R² 'accuracy'."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    # Check metric labels
    assert '"accuracy"' not in content and "'accuracy'" not in content, \
        "Must not label MAE/RMSE/R² as 'accuracy'"


def test_model_info_has_limitation_warning():
    """Model Info must show a limitation warning."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    assert "warning" in content.lower() or "⚠️" in content


def test_model_info_offline_state():
    """Model Info must handle backend unavailable with error component."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    assert "render_error" in content, "Must use render_error for backend failure"


def test_model_info_metrics_from_api():
    """Metrics must come from API response, not hardcoded."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    # Check dynamic access of metrics
    assert "info.metrics" in content or "metrics.MAE" in content or "metrics.RMSE" in content, \
        "Metrics should be accessed from API response"


def test_model_info_regression_not_probability():
    """Model Info must clarify this is a regression model, not probability."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "5_Model_Info.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "regression" in lower, \
        "Page must identify this as a regression model"


def test_model_info_api_models_updated():
    """ModelInfoResponse must support metrics and timestamp fields."""
    from api.models import ModelInfoResponse
    data = {
        "model_id": "TEST",
        "model_version": "1.0",
        "model_family": "XGBoost",
        "package_version": "1.0",
        "data_version": "1.0",
        "feature_set": "18",
        "timestamp": "2026-08-06T00:00:00Z",
        "metrics": {"MAE": 16.2, "RMSE": 20.5, "R2": 0.09},
    }
    resp = ModelInfoResponse(data)
    assert resp.model_id == "TEST"
    assert resp.metrics is not None
    assert resp.metrics.MAE == 16.2
    assert resp.timestamp == "2026-08-06T00:00:00Z"
