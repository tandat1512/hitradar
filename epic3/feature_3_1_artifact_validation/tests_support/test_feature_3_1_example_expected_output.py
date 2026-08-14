"""Test: Example Expected Output — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_example_prediction_result.json"

def test_prediction_matches_expected():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_matches_expected"] == True
    assert data["absolute_difference"] == 0.0

def test_expected_prediction():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["expected_prediction"] == 46.421062

def test_tolerance():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["tolerance"] == 0.001
