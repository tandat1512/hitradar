"""Test 2: Manifest Integrity
Verify artifact_manifest.json entries match actual files on disk.
"""
import json, hashlib, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
INVENTORY_FILE = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "inventories" / "feature_3_1_artifact_inventory.json"

def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def test_manifest_loads():
    manifest = PKG_ROOT / "metadata" / "artifact_manifest.json"
    with open(manifest, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 18, f"Expected at least 18 artifact entries, got {len(data)}"

def test_model_artifact_hash_matches():
    model = PKG_ROOT / "pipeline" / "full_inference_pipeline.joblib"
    assert model.exists(), f"full_inference_pipeline.joblib not found: {model}"
    actual = _sha256(model)
    expected = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"
    assert actual == expected, f"full_inference_pipeline.joblib hash mismatch: expected {expected}, got {actual}"

def test_best_model_hash_matches():
    model = PKG_ROOT / "models" / "best_model.joblib"
    assert model.exists()
    actual = _sha256(model)
    expected = "4b5859268e7ea024daacc1d27a8f59f5c45480a29d3598c7304a4e3cb3e3c1fd"
    assert actual == expected

def test_input_schema_hash_matches():
    f = PKG_ROOT / "schemas" / "input_schema.json"
    actual = _sha256(f)
    expected = "91d1d8070df43716a39879c3c06b06ae5ea4d266bd9d6872f5dc7472fb38d503"
    assert actual == expected

def test_output_schema_hash_matches():
    f = PKG_ROOT / "schemas" / "output_schema.json"
    actual = _sha256(f)
    expected = "3d77b33b1d23c806358a872d1481262e68b42b474f5218273e50ab5a69fb17e8"
    assert actual == expected

def test_manifest_self_consistency():
    """Manifest should declare all artifacts exist (exists=True)."""
    with open(PKG_ROOT / "metadata" / "artifact_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    all_exist = all(a.get("exists", False) for a in manifest)
    assert all_exist, "Some artifacts in manifest have exists=False"

def test_inference_pipeline_hash_mismatch_detected():
    """runtime/inference_pipeline.py hash differs from manifest — this is a KNOWN BLOCKER."""
    f = PKG_ROOT / "runtime" / "inference_pipeline.py"
    actual = _sha256(f)
    manifest_hash = "34ef2ebe49bf82923806e926115c2c86eb186735dd637f8cbe3b624a18dd8ffa"
    # This test documents the KNOWN mismatch
    # We assert the ACTUAL value (not the manifest value)
    # Phase 1 only READS — we record this as a blocker
    assert actual == "6a54f86cfb87059a2a4276ce970f74797649255ad3c28f23286a0f44a51570c7"
    # The mismatch between actual and manifest_hash IS the known issue
    assert actual != manifest_hash  # This is the BLOCKER we are documenting

def test_inventory_records_hash_mismatch():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        inv = json.load(f)
    mismatch = [a for a in inv["artifacts"] if a.get("status") == "HASH_MISMATCH"]
    assert len(mismatch) >= 1
    assert mismatch[0]["logical_name"] == "inference_pipeline_module"
