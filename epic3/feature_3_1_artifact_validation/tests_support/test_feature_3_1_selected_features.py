"""Test: Selected Features
Verify selected_features.json is valid.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
SF_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_selected_features_validation.json"
SF_FILE = PKG_ROOT / "schemas/selected_features.json"

def _load_sf():
    with open(SF_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_val():
    with open(SF_VAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_file_exists():
    assert SF_FILE.exists()

def test_parseable():
    data = _load_sf()
    assert isinstance(data, dict)

def test_feature_set_id():
    data = _load_sf()
    assert data["feature_set_id"] == "FS23-SELECTED"

def test_feature_count():
    data = _load_sf()
    assert data["feature_count"] == 31

def test_features_list_count():
    data = _load_sf()
    assert len(data["features"]) == 31

def test_validation_file():
    data = _load_val()
    assert data["validation_status"] == "PASS"

def test_no_empty_names():
    data = _load_sf()
    assert all(f for f in data["features"])

def test_no_duplicates():
    import collections
    data = _load_sf()
    counts = collections.Counter(data["features"])
    dupes = [k for k, v in counts.items() if v > 1]
    assert dupes == [], f"Duplicate feature names: {dupes}"

def test_target_excluded():
    data = _load_sf()
    assert "target_popularity" not in data["features"]
    assert "target" not in data["features"]

def test_track_id_excluded():
    data = _load_sf()
    assert "track_id" not in data["features"]

def test_layer_classification():
    data = _load_val()
    assert data["layer_classification"] == "SELECTED_ENGINEERED_FEATURES"
