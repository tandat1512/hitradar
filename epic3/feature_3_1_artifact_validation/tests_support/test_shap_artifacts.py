"""Test 9: SHAP Artifacts
Verify SHAP explainability artifacts exist in 7.ML/7.9.explainability/.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
SHAP_ROOT = REPO_ROOT / "7.ML" / "7.9.explainability"
READABILITY_FILE = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "inventories" / "feature_3_1_artifact_readability.json"

def test_shap_root_exists():
    assert SHAP_ROOT.exists(), f"SHAP root not found: {SHAP_ROOT}"

def test_champion_explainability_lock_exists():
    f = SHAP_ROOT / "manifests" / "champion_explainability_lock.json"
    assert f.exists(), f"champion_explainability_lock.json not found: {f}"

def test_global_explanation_summary_exists():
    f = SHAP_ROOT / "global" / "global_explanation_summary.json"
    assert f.exists(), f"global_explanation_summary.json not found"

def test_shap_top_10_features_exists():
    f = SHAP_ROOT / "global" / "shap_top_10_features.json"
    assert f.exists()

def test_local_explanation_manifest_exists():
    f = SHAP_ROOT / "local" / "local_explanation_manifest.json"
    assert f.exists()

def test_shap_config_exists():
    f = SHAP_ROOT / "configs" / "feature_2_6_shap_config.json"
    assert f.exists()

def test_shap_summary_images_exist():
    img_files = list((SHAP_ROOT / "global").glob("shap_summary_*.png"))
    assert len(img_files) >= 3, f"Expected at least 3 SHAP summary images, found {len(img_files)}"

def test_shap_waterfall_images_exist():
    waterfall_files = list((SHAP_ROOT / "local").glob("local_case_*.png"))
    assert len(waterfall_files) >= 5, f"Expected at least 5 waterfall images, found {len(waterfall_files)}"

def test_global_explanation_summary_valid():
    f = SHAP_ROOT / "global" / "global_explanation_summary.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict)
    assert len(data) > 0

def test_shap_readability_report():
    with open(READABILITY_FILE, "r", encoding="utf-8") as f:
        rep = json.load(f)
    shap = rep["shap_artifacts_discovered"]
    assert shap["total_shap_artifacts"] >= 100
    assert shap["shap_explainability_status"] == "FOUND_AND_READABLE"
