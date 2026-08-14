"""Test: SHAP Inventory — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
INV_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_shap_asset_inventory.json"

def test_inventory_status():
    with open(INV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["summary"]["found_assets"] == 16
    assert data["summary"]["missing_assets"] == 0

def test_shap_required_for_epic3():
    with open(INV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["shap_required_for_epic3"] == True

def test_all_required_assets_found():
    with open(INV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    required = [a for a in data["assets"] if a["required"]]
    assert len(required) > 0
    assert all(a["status"] == "FOUND" for a in required)

def test_shap_values_found():
    with open(INV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    vals = next((a for a in data["assets"] if a["role"] == "SHAP_values_global"), None)
    assert vals is not None
    assert vals["status"] == "FOUND"

def test_shap_background_transformed_found():
    with open(INV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    bg = next((a for a in data["assets"] if a["role"] == "SHAP_background_transformed"), None)
    assert bg is not None
    assert bg["status"] == "FOUND"
    assert bg["columns"] == 49

def test_additivity_validation_found():
    with open(INV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    add = next((a for a in data["assets"] if a["role"] == "SHAP_additivity_validation"), None)
    assert add is not None
    assert add["status"] == "FOUND"
