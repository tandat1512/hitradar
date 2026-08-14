"""Test: Benchmark Timer — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
CFG_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_config.json"

def test_uses_perf_counter():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "perf_counter" in data["timer"]
