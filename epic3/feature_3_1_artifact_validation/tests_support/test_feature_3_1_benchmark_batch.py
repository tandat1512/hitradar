"""Test: Benchmark Batch — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
RES_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json"

def test_batch_results_present():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["batch_results"] is not None
    assert len(data["batch_results"]) > 0

def test_batch_1_present():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "1" in data["batch_results"]
    assert data["batch_results"]["1"]["per_record_median_ms"] > 0

def test_batch_100_present():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "100" in data["batch_results"]

def test_batch_per_record_median_reasonable():
    """Per-record latency should be consistent across batch sizes."""
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    b1 = data["batch_results"]["1"]["per_record_median_ms"]
    b100 = data["batch_results"]["100"]["per_record_median_ms"]
    # Per-record should be roughly similar (within 3x)
    assert b100 < b1 * 3
