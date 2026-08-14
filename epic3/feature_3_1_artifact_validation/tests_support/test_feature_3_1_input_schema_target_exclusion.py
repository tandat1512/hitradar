"""Test: Input Schema Target Exclusion
Verify target_popularity and track_id are NOT in the 18 input fields.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
INP_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_input_schema_validation.json"

def test_target_not_in_raw_fields():
    with open(INP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    field_names = [f["name"] for f in data["fields"]]
    assert "target_popularity" not in field_names
    assert "target" not in field_names
    assert "popularity" not in field_names

def test_track_id_not_in_raw_fields():
    with open(INP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    field_names = [f["name"] for f in data["fields"]]
    assert "track_id" not in field_names
    assert "track" not in field_names

def test_feature_contract_consistency_target_excluded():
    import json
    with open(INP_VAL_FILE, "r", encoding="utf-8") as f:
        inp = json.load(f)
    with open(REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_feature_contract_consistency.json", "r", encoding="utf-8") as f:
        fcc = json.load(f)
    # consistency_checks[2] is target_excluded
    assert fcc["consistency_checks"][2]["status"] in ("PASS", "PASS_WITH_NOTE")
