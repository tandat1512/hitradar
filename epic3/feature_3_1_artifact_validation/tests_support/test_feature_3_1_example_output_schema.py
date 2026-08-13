"""Test: Example Output Schema — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_example_output_validation.json"

def test_validation_status():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_prediction_raw():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["actual_output"]["prediction_raw"] == 46.421062

def test_prediction_clipped():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["actual_output"]["prediction_clipped"] == 46.421062

def test_prediction_display():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["actual_output"]["prediction_display"] == 46

def test_finite_prediction():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["finite_prediction_check"]["status"] == "PASS"

def test_clipped_display_consistency():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["raw_clipped_display_consistency"]["status"] == "PASS"

def test_model_version_check():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_version_check"]["status"] == "PASS"
    assert data["model_version_check"]["match"] == True

def test_no_blockers():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["blockers"] == []
