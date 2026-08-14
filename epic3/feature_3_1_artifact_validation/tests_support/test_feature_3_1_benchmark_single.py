"""Test: Benchmark Single — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
RES_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json"

def test_warm_single_measured():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["warm_single_prediction"]["count"] >= 100

def test_warm_single_has_p95():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "p95_ms" in data["warm_single_prediction"]

def test_warm_single_has_p99():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "p99_ms" in data["warm_single_prediction"]

def test_warm_single_median_positive():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["warm_single_prediction"]["median_ms"] > 0

def test_warm_single_usable_for_development():
    """Median < 100ms means usable for local development."""
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["warm_single_prediction"]["median_ms"] < 100
