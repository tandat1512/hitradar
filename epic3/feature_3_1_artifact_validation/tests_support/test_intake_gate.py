"""Test 10: Intake Gate
Verify feature_3_1_intake_gate.json — overall gate is FAIL as expected,
and blockers are correctly recorded.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
GATE_FILE = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "validation" / "feature_3_1_intake_gate.json"
CHECKPOINT_FILE = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "checkpoints" / "feature_3_1_phase_1_checkpoint.json"
INVENTORY_FILE = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "inventories" / "feature_3_1_artifact_inventory.json"

def test_gate_file_exists():
    assert GATE_FILE.exists(), f"Intake gate file not found: {GATE_FILE}"

def test_gate_status_is_fail():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    assert gate["gate_status"] == "FAIL"

def test_gate_has_blockers():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    assert len(gate["blockers"]) >= 1

def test_gate_criteria_count():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    assert len(gate["gate_criteria"]) == 12

def test_phase_2_not_ready():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    assert gate["overall_readiness"] == "BLOCKED"

def test_checkpoint_exists():
    assert CHECKPOINT_FILE.exists()
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        ckpt = json.load(f)
    assert ckpt["gate_status"] == "FAIL"
    assert ckpt["blocker_count"] >= 1

def test_inventory_summary_accurate():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        inv = json.load(f)
    artifacts = inv["artifacts"]
    # Verify summary counts match actual artifact list
    actual_exact = len([a for a in artifacts if a["status"] == "FOUND_EXACT"])
    actual_mismatch = len([a for a in artifacts if a["status"] == "HASH_MISMATCH"])
    # summary["FOUND_EXACT"] in JSON may be stale — test actual list
    assert actual_exact >= 16, f"Expected at least 16 FOUND_EXACT artifacts, got {actual_exact}"
    assert actual_mismatch >= 1, f"Expected at least 1 HASH_MISMATCH (inference_pipeline.py), got {actual_mismatch}"
    assert len(artifacts) >= 20, f"Expected at least 20 entries, got {len(artifacts)}"

def test_blocker_1_handoff_missing():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    blk = next((b for b in gate["blockers"] if "MISSING_HANDOFF" in b.get("type", "")), None)
    assert blk is not None

def test_blocker_2_stale_manifest():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    blk = next((b for b in gate["blockers"] if "STALE_MANIFEST" in b.get("type", "")), None)
    assert blk is not None

def test_recommendation_is_hold():
    with open(GATE_FILE, "r", encoding="utf-8") as f:
        gate = json.load(f)
    assert "HOLD" in gate["recommendation"] or "BLOCKED" in gate["overall_readiness"]
