"""Test: Residual Convention — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_residual_stats_validation.json"

def test_convention_defined():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["residual_convention"]["defined"] == True

def test_convention_not_explicitly_documented():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["residual_convention"]["explicit"] == False

def test_convention_inferred_correctly():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "actual" in data["residual_convention"]["definition"]
    assert "predicted" in data["residual_convention"]["definition"]
    assert "-" in data["residual_convention"]["definition"]

def test_warning_for_implicit_convention():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    warning_types = [w["type"] for w in data["warnings"]]
    assert "RESIDUAL_CONVENTION_NOT_EXPLICITLY_DOCUMENTED" in warning_types

def test_mean_positive_means_underprediction():
    """Under residual convention (actual - predicted): positive mean = systematic underprediction."""
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["residual_statistics"]["mean"] > 0
    assert data["interpretation"]["underprediction_rate"] > 0.5
