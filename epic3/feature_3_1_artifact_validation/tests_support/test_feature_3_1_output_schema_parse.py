"""Test: Output Schema Parse
Verify output_schema.json parses correctly.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
OUT_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_output_schema_validation.json"
OUTPUT_SCHEMA_FILE = PKG_ROOT / "schemas/output_schema.json"

def test_output_schema_file_exists():
    assert OUTPUT_SCHEMA_FILE.exists()

def test_output_schema_parseable():
    with open(OUTPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)

def test_schema_id():
    with open(OUTPUT_SCHEMA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_id"] == "HITRADAR-PREDICTION-OUTPUT-V1"

def test_validation_file_valid():
    with open(OUT_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["parse_status"] == "OK"
    assert data["validation_status"] == "PASS"

def test_field_count_8():
    with open(OUT_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["field_count"] == 8
