"""Test: SHAP Assets — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_shap_asset_validation.json"

def test_shap_validation_status_pass():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_shap_recomputed_false():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["shap_recomputed"] == False

def test_all_asset_validations_pass():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    failed = [a for a in data["asset_validations"] if a["status"] != "PASS"]
    assert failed == [], f"Failed: {[a['role'] for a in failed]}"

def test_feature_dimension_consistent():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["feature_dimension_consistency"]["all_match"] == True
    assert data["feature_dimension_consistency"]["background_transformed_cols"] == 49
    assert data["feature_dimension_consistency"]["shap_values_cols"] == 49

def test_model_version_consistent():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_version_consistency"]["status"] == "PASS"

def test_additivity_pass_rate():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    add = next(a for a in data["asset_validations"] if a["role"] == "SHAP_additivity")
    assert add["additivity_pass_rate"] == 1.0

def test_no_blockers():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["blockers"] == []
