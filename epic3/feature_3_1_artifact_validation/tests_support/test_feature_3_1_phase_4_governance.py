"""Test: Phase 4 Governance — no SLA claimed"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
RES_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json"

def test_no_sla_claimed():
    """Phase 4 spec explicitly forbids claiming this is a production SLA."""
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["target_latency_defined"] == False
    assert data["target_latency_met"] is None

def test_benchmark_scope_is_local():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["benchmark_scope"] == "LOCAL_INFERENCE"

def test_training_not_executed():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False
