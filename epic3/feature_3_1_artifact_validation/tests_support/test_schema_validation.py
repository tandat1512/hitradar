"""Test 3: Schema Validation
Verify all schema JSON files are valid and parse correctly.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"

def test_input_schema_valid_json():
    f = PKG_ROOT / "schemas" / "input_schema.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["schema_id"] == "HITRADAR-PREDICTION-INPUT-V1"
    assert data["schema_version"] == "1.0.0"

def test_input_schema_has_18_fields():
    f = PKG_ROOT / "schemas" / "input_schema.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert len(data["fields"]) == 18

def test_output_schema_valid_json():
    f = PKG_ROOT / "schemas" / "output_schema.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["schema_id"] == "HITRADAR-PREDICTION-OUTPUT-V1"
    required_fields = ["status", "prediction_raw", "prediction_clipped", "prediction_display"]
    schema_fields = [f["name"] for f in data["fields"]]
    for req in required_fields:
        assert req in schema_fields

def test_selected_features_valid():
    f = PKG_ROOT / "schemas" / "selected_features.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["feature_set_id"] == "FS23-SELECTED"
    assert data["feature_count"] == 31
    assert len(data["features"]) == 31

def test_feature_names_valid():
    f = PKG_ROOT / "schemas" / "feature_names.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["model_matrix_width"] == 49
    assert data["feature_name_count"] == 49
    assert len(data["feature_names"]) == 49

def test_feature_mapping_valid():
    f = PKG_ROOT / "schemas" / "feature_mapping.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, list)
    assert len(data) == 49
    all_confirmed = all(m.get("mapping_status") == "CONFIRMED" for m in data)
    assert all_confirmed

def test_model_version_valid():
    f = PKG_ROOT / "metadata" / "model_version.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["model_id"] == "EXP24-XGB-FINAL-001"
    assert data["model_version"] == "1.0.0"
    assert data["model_family"] == "XGBoost"

def test_package_version_valid():
    f = PKG_ROOT / "metadata" / "package_version.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["package_version"] == "2.7.0"

def test_data_version_valid():
    f = PKG_ROOT / "metadata" / "data_version.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["data_version"] == "1.0.0"
