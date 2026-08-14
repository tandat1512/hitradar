"""Test: Input Schema Parse
Verify input_schema.json parses correctly.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
INP_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_input_schema_validation.json"
INPUT_SCHEMA_FILE = PKG_ROOT / "schemas/input_schema.json"

def test_input_schema_file_exists():
    assert INPUT_SCHEMA_FILE.exists()

def test_input_schema_parseable():
    with open(INPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)

def test_schema_id():
    with open(INPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_id"] == "HITRADAR-PREDICTION-INPUT-V1"

def test_schema_version():
    with open(INPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == "1.0.0"

def test_has_fields_key():
    with open(INPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "fields" in data
    assert isinstance(data["fields"], list)

def test_additional_properties_policy():
    with open(INPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("additional_properties_policy") == "IGNORE_WITH_WARNING"

def test_validation_file_valid():
    with open(INP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["parse_status"] == "OK"
    assert data["validation_status"] == "PASS"

def test_field_count_18():
    with open(INP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["field_count_actual"] == 18
