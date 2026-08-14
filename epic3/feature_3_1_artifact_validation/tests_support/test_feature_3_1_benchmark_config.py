"""Test: Benchmark Config — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
CFG_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_config.json"

def test_config_file_exists():
    assert CFG_FILE.exists()

def test_timer_is_perf_counter():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["timer"] == "time.perf_counter_ns"

def test_warm_up_defined():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["warm_up_iterations"] >= 5

def test_measured_single_defined():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["measured_single_iterations"] >= 100

def test_fresh_process_load_runs():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["fresh_process_load_runs"] >= 3

def test_batch_sizes_defined():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert 1 in data["batch_sizes"]
    assert 100 in data["batch_sizes"]

def test_gc_policy_disabled():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "disabled" in data["garbage_collection_policy"].lower()

def test_input_source_canonical():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "example_input" in data["input_source"].lower()
