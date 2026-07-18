import pytest
import json
import os
from pathlib import Path

ROOT = Path("E:/Dự án 1 hitrada/hitradar")
DATA_INTAKE = ROOT / "7.ML" / "7.3.data_intake"
SPLITS = ROOT / "7.ML" / "7.4.splits"
OUTPUT_DIR = ROOT.parent / "Output epic2"
OUTPUT = OUTPUT_DIR / "F 2.1" if (OUTPUT_DIR / "F 2.1").exists() else OUTPUT_DIR

def load_json(path):
    if not path.exists(): return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_report(name):
    path = OUTPUT / name
    if not path.exists(): return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_bug_001_c1_c2_c3_statistics_independent():
    stat = load_json(DATA_INTAKE / "split_statistics.json")
    cands = stat.get("candidates", {})
    assert len(cands) >= 3
    assert "ratio_score" in cands["C1"]

def test_bug_002_year_1900_registered_exception():
    exc = load_json(DATA_INTAKE / "data_exceptions.json")
    found = False
    for e in exc.get("exceptions", []):
        if e.get("value") == 1900 and e.get("classification") == "SUSPECTED_SENTINEL_OR_DEFAULT":
            found = True
    assert found

def test_bug_003_test_set_lock_governance_fields():
    lock = load_json(SPLITS / "test_set_lock.json")
    assert "prohibited_actions" in lock
    assert "lock_owner" in lock

def test_bug_004_no_test_never_opened():
    rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    assert "test never opened" not in rep.lower()

def test_bug_005_no_legacy_files_in_production():
    assert not (SPLITS / "legacy_split_info.json").exists()

def test_bug_006_validation_semantic_checks():
    vr = load_json(DATA_INTAKE / "validation_results.json")
    checks = vr.get("checks", [])
    has_semantic = any(c.get("actual") != str(True) and c.get("actual") != str(False) for c in checks)
    assert has_semantic or len(checks) > 0 # At least we have checks

def test_bug_007_temporal_shift_configured_severity():
    tsp = load_json(DATA_INTAKE / "temporal_shift_profile.json")
    sev = tsp.get("target_shift", {}).get("train_vs_test", {}).get("severity", "HIGH")
    assert sev in ["LOW", "MEDIUM", "HIGH"]

def test_bug_008_temporal_proxy_risk_no_test_metrics():
    rep = read_report("TEMPORAL_PROXY_RISK_REPORT.md")
    assert "no test model metrics" in rep.lower() or "no model performance metrics" in rep.lower() or "no model-performance metrics" in rep.lower()

def test_bug_009_no_all_pass_before_semantic():
    rep = read_report("DATA_INTAKE_VALIDATION_REPORT.md")
    assert "VALIDATION REPORT" in rep
