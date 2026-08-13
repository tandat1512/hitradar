"""Test: Output Schema Fields
Verify all output fields have correct types.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
OUT_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_output_schema_validation.json"

def _load():
    with open(OUT_VAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_all_fields_pass():
    data = _load()
    for f in data["fields"]:
        assert f["validation_status"] == "PASS", f"Field {f['name']} failed"

def test_status_field():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "status")
    assert f["type"] == "string"

def test_prediction_raw_type():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "prediction_raw")
    assert f["type"] == "number"

def test_prediction_clipped_type():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "prediction_clipped")
    assert f["type"] == "number"

def test_prediction_display_type():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "prediction_display")
    assert f["type"] == "integer"

def test_model_id_field():
    data = _load()
    field_names = [f["name"] for f in data["fields"]]
    assert "model_id" in field_names

def test_warnings_field():
    data = _load()
    field_names = [f["name"] for f in data["fields"]]
    assert "warnings" in field_names
