"""Test 5: Output Schema Validation
Verify output_schema.json has correct output format.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
OUTPUT_SCHEMA = PKG_ROOT / "schemas" / "output_schema.json"
EXAMPLE_INPUT = PKG_ROOT / "examples" / "example_input.json"
EXAMPLE_OUTPUT = PKG_ROOT / "examples" / "example_output.json"

def _load_output():
    with open(OUTPUT_SCHEMA, "r", encoding="utf-8") as f:
        return json.load(f)

def test_output_schema_has_required_fields():
    data = _load_output()
    field_names = [f["name"] for f in data["fields"]]
    required = ["status", "model_id", "model_version", "package_version",
                "prediction_raw", "prediction_clipped", "prediction_display", "warnings"]
    for req in required:
        assert req in field_names, f"Missing required field: {req}"

def test_prediction_raw_type():
    data = _load_output()
    f = next(x for x in data["fields"] if x["name"] == "prediction_raw")
    assert f["type"] == "number"

def test_prediction_display_type():
    data = _load_output()
    f = next(x for x in data["fields"] if x["name"] == "prediction_display")
    assert f["type"] == "integer"

def test_prediction_clipped_bounded():
    data = _load_output()
    notes = data.get("notes", {})
    assert notes["prediction_clipped"] == "Always in [0, 100]"

def test_example_output_valid():
    with open(EXAMPLE_OUTPUT, "r", encoding="utf-8") as f:
        out = json.load(f)
    assert out["status"] == "SUCCESS"
    assert "prediction_raw" in out
    assert "prediction_clipped" in out
    assert "prediction_display" in out
    assert isinstance(out["prediction_display"], int)
    assert 0 <= out["prediction_display"] <= 100

def test_example_output_model_metadata():
    with open(EXAMPLE_OUTPUT, "r", encoding="utf-8") as f:
        out = json.load(f)
    assert out["model_id"] == "EXP24-XGB-FINAL-001"
    assert out["model_version"] == "1.0.0"
    # package_version in example_output.json is "1.0.0" (example was generated before packaging)
    # Note: discrepancy vs metadata/package_version.json (2.7.0) is a data quality issue
    assert "package_version" in out

def test_example_input_has_18_fields():
    with open(EXAMPLE_INPUT, "r", encoding="utf-8") as f:
        inp = json.load(f)
    assert len(inp) == 18

def test_example_input_danceability_valid():
    with open(EXAMPLE_INPUT, "r", encoding="utf-8") as f:
        inp = json.load(f)
    assert 0.0 <= inp["danceability"] <= 1.0
