"""Test 4: Input Schema Deep Validation
Verify input_schema.json has correct field types, ranges, and defaults.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
INPUT_SCHEMA = PKG_ROOT / "schemas" / "input_schema.json"

def _load():
    with open(INPUT_SCHEMA, "r", encoding="utf-8") as f:
        return json.load(f)

def test_field_count():
    data = _load()
    assert len(data["fields"]) == 18

def test_all_fields_required():
    data = _load()
    not_required = [f["name"] for f in data["fields"] if not f.get("required", False)]
    assert not_required == [], f"Fields not required: {not_required}"

def test_all_fields_nullable():
    data = _load()
    not_nullable = [f["name"] for f in data["fields"] if not f.get("nullable", False)]
    assert not_nullable == [], f"Fields not nullable: {not_nullable}"

def test_danceability_range():
    data = _load()
    d = next(f for f in data["fields"] if f["name"] == "danceability")
    assert d["minimum"] == 0.0
    assert d["maximum"] == 1.0
    assert d["data_type"] == "number"

def test_energy_range():
    data = _load()
    e = next(f for f in data["fields"] if f["name"] == "energy")
    assert e["minimum"] == 0.0
    assert e["maximum"] == 1.0

def test_tempo_range():
    data = _load()
    t = next(f for f in data["fields"] if f["name"] == "tempo")
    assert t["minimum"] == 0.0
    assert t["maximum"] == 300.0

def test_loudness_range():
    data = _load()
    l = next(f for f in data["fields"] if f["name"] == "loudness")
    assert l["minimum"] == -60.0
    assert l["maximum"] == 0.0

def test_release_year_range():
    data = _load()
    y = next(f for f in data["fields"] if f["name"] == "release_year")
    assert y["minimum"] == 1900
    assert y["maximum"] == 2100

def test_release_month_range():
    data = _load()
    m = next(f for f in data["fields"] if f["name"] == "release_month")
    assert m["minimum"] == 1
    assert m["maximum"] == 12

def test_explicit_is_boolean():
    data = _load()
    e = next(f for f in data["fields"] if f["name"] == "explicit")
    assert e["data_type"] == "boolean"
    assert e["allowed_categories"] == ["False", "True"]

def test_release_precision_categories():
    data = _load()
    rp = next(f for f in data["fields"] if f["name"] == "release_precision")
    assert rp["allowed_categories"] == ["day", "month", "year"]

def test_key_range():
    data = _load()
    k = next(f for f in data["fields"] if f["name"] == "key")
    assert k["minimum"] == 0
    assert k["maximum"] == 11

def test_time_signature_categories():
    data = _load()
    ts = next(f for f in data["fields"] if f["name"] == "time_signature")
    assert set(ts["allowed_categories"]) == {"1.0", "3.0", "4.0", "5.0"}

def test_all_fields_have_default_policy():
    data = _load()
    no_default = [f["name"] for f in data["fields"] if f.get("default_policy") is None]
    assert no_default == []

def test_canonical_field_order():
    """Verify canonical input field order matches API contract."""
    data = _load()
    expected_order = [
        "duration_min", "explicit", "release_year", "release_month",
        "decade", "release_precision", "danceability", "energy", "key",
        "loudness", "mode", "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo", "time_signature"
    ]
    actual_order = [f["name"] for f in data["fields"]]
    assert actual_order == expected_order, f"Field order mismatch:\nExpected: {expected_order}\nActual:   {actual_order}"
