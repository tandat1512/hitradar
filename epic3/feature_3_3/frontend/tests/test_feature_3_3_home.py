"""Test Home page — Feature 3.3 Phase 3"""
import pytest


def test_home_no_model_import():
    """Home page must not import backend services or model libs."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "0_Home.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["joblib", "pickle", "ModelService", "ExplainService",
                 "WhatIfService", "from app.", "xgboost"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 0_Home.py"


def test_home_has_no_commercial_claim():
    """Home must not claim to be a commercial production system."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "0_Home.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "commercial" not in lower or "not commercial" in lower, \
        "Home must not claim commercial use"


def test_home_has_research_prototype_disclaimer():
    """Home must mention this is a research/student project."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "0_Home.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "research" in lower or "student" in lower, \
        "Home must mention this is a research/student project"


def test_home_has_limitation_warning():
    """Home must show a limitation warning."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "0_Home.py")
    content = open(path, encoding="utf-8").read()
    assert "warning" in content.lower() or "⚠️" in content


def test_home_no_backend_dependency_on_load():
    """Home should not crash if backend is offline."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "0_Home.py")
    content = open(path, encoding="utf-8").read()
    # Home should not call API on import
    assert "client.get_features()" not in content
    assert "client.health()" not in content


def test_home_renders_static_content():
    """Home must have static project description content."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "0_Home.py")
    content = open(path, encoding="utf-8").read()
    assert "HitRadar Pro" in content
    assert "popularity" in content.lower()
