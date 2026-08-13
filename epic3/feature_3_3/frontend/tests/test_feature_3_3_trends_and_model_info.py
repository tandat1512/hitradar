"""Test Music Trends page — Feature 3.3 Phase 5"""
import pytest
import os


def test_trends_no_model_import():
    """Trends page must not import model libs or backend services."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["joblib", "ModelService", "ExplainService", "WhatIfService",
                "from app.", "xgboost", "pickle", "from api import"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 4_Trends.py"


def test_trends_no_train_or_refit():
    """Trends page must not train or refit."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    forbidden = [".fit", ".train(", "train_model", "refit"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 4_Trends.py"


def test_trends_uses_dataset():
    """Trends must source from ml_ready_dataset.csv."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    assert "ml_ready_dataset.csv" in content, "Must reference ml_ready_dataset.csv"


def test_trends_uses_yearly_evaluation():
    """Trends must source from yearly_evaluation.csv."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    assert "yearly_evaluation.csv" in content, "Must reference yearly_evaluation.csv"


def test_trends_uses_cached_data():
    """Trend data loading must use st.cache_data."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    assert "st.cache_data" in content, "Must use st.cache_data for data loading"


def test_trends_no_source_mutation():
    """Trends must not write to source data files."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    assert "open(" not in content or "r" in content, \
        "Must not open source data in write mode"
    forbidden = ["w", "a", "x"]  # write modes
    for line in content.splitlines():
        if "open(" in line and not line.strip().startswith("#"):
            for mode in forbidden:
                assert mode not in line, \
                    f"Source file opened in write mode: {line.strip()}"


def test_trends_has_causal_disclaimer():
    """Trends page must show causal disclaimer."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "not causal" in lower or "correlation" in lower or "causal" in lower, \
        "Trends page must include causal disclaimer"


def test_trends_has_limitation_warning():
    """Trends page must include a limitation warning."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    assert "warning" in content.lower() or "⚠️" in content


def test_trends_dataset_path_resolved():
    """Trends must resolve dataset path relative to repo root, not hardcoded absolute."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    # Path should be constructed from __file__, not hardcoded
    assert "_REPO_ROOT" in content or "os.path.join" in content, \
        "Dataset path should be resolved relative to repo root"
