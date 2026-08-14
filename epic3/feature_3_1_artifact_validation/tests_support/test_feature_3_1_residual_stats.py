"""Test: Residual Statistics — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_residual_stats_validation.json"

def test_validation_status_pass():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_residual_convention_defined():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["residual_convention"]["defined"] == True

def test_residual_mean_positive():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["residual_statistics"]["mean"] > 0

def test_residual_all_finite():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["residual_statistics"]["all_finite"] == True
    assert data["absolute_error_statistics"]["all_finite"] == True

def test_ae_mean_equals_mae():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    ae_mean = data["absolute_error_statistics"]["mean"]
    import math
    assert abs(ae_mean - 17.646684299211866) < 1e-6

def test_sample_rows_match_test():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["sample_rows"] == 85876

def test_underprediction_rate_reasonable():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    rate = data["interpretation"]["underprediction_rate"]
    assert 0.0 <= rate <= 1.0
    assert rate > 0.5  # model underpredicts majority of the time

def test_positive_mean_with_high_underprediction_consistent():
    """Positive mean residual + high underprediction rate should be consistent."""
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    mean_pos = data["residual_statistics"]["mean"] > 0
    underpred_rate = data["interpretation"]["underprediction_rate"]
    consistent = mean_pos and (underpred_rate > 0.5)
    assert consistent, "Positive mean residual should correlate with high underprediction rate"
