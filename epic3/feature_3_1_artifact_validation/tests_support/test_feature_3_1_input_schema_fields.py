"""Test: Input Schema Fields
Verify all 18 fields have correct types, ranges, and defaults.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
INP_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_input_schema_validation.json"

def _load():
    with open(INP_VAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_all_fields_pass():
    data = _load()
    for f in data["fields"]:
        assert f["validation_status"] == "PASS", f"Field {f['name']} failed"

def test_field_count_18():
    data = _load()
    assert len(data["fields"]) == 18

def test_all_required():
    data = _load()
    assert all(f["required"] for f in data["fields"])

def test_all_nullable():
    data = _load()
    assert all(f["nullable"] for f in data["fields"])

def test_all_have_default_policy():
    data = _load()
    assert all(f.get("default_policy") == "PIPELINE_IMPUTE" for f in data["fields"])

def test_danceability_range():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "danceability")
    assert f["minimum"] == 0.0 and f["maximum"] == 1.0

def test_tempo_range():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "tempo")
    assert f["minimum"] == 0.0 and f["maximum"] == 300.0

def test_loudness_range():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "loudness")
    assert f["minimum"] == -60.0 and f["maximum"] == 0.0

def test_release_month_range():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "release_month")
    assert f["minimum"] == 1 and f["maximum"] == 12

def test_release_precision_categories():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "release_precision")
    assert set(f["allowed_categories"]) == {"day", "month", "year"}

def test_key_range():
    data = _load()
    f = next(x for x in data["fields"] if x["name"] == "key")
    assert f["minimum"] == 0 and f["maximum"] == 11

def test_canonical_order():
    data = _load()
    expected = ["duration_min","explicit","release_year","release_month","decade",
                "release_precision","danceability","energy","key","loudness","mode",
                "speechiness","acousticness","instrumentalness","liveness","valence",
                "tempo","time_signature"]
    actual = [f["name"] for f in data["fields"]]
    assert actual == expected
