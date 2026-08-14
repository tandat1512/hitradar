"""Test: SHAP Model Version — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_shap_asset_validation.json"

def test_model_version_consistent():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_version_consistency"]["champion_id_from_manifest"] == "EXP24-XGB-FINAL-001"
    assert data["model_version_consistency"]["champion_id_from_shap_manifest"] == "EXP24-XGB-FINAL-001"
    assert data["model_version_consistency"]["status"] == "PASS"
