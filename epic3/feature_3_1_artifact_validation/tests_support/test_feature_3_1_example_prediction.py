"""Test: Example Prediction — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_example_prediction_result.json"

def test_prediction_executed():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_executed"] == True

def test_prediction_matches_expected():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_matches_expected"] == True
    assert data["absolute_difference"] < 0.001

def test_prediction_raw():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_raw"] == 46.421062

def test_prediction_clipped():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_clipped"] == 46.421062

def test_prediction_display():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_display"] == 46

def test_status_pass():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "PASS"

def test_model_version_matches():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_version_matches"] == True

def test_no_nan_inf():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["has_nan"] == False
    assert data["has_inf"] == False

def test_hash_unchanged():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_unchanged"] == True

def test_no_fit_calls():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["fit_call_count_after_predictions"] == 0
    assert data["fit_transform_count_after_predictions"] == 0
    assert data["partial_fit_count_after_predictions"] == 0
