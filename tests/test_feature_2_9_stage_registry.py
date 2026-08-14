import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_registry_exists():
    assert (F29 / "registries" / "epic2_pipeline_stage_registry.json").exists()

def test_stage_count():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 14

def test_only_p50_can_train():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        data = json.load(f)
    train_stages = [s["stage_id"] for s in data if s.get("can_train")]
    assert train_stages == ["P50_TRAIN_CANDIDATES"], f"Unexpected training stages: {train_stages}"

def test_only_p70_uses_final_test():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        data = json.load(f)
    ft = [s["stage_id"] for s in data if s.get("can_use_final_test_labels")]
    assert ft == ["P70_FINAL_TEST"], f"Unexpected final test stages: {ft}"

def test_p90_cannot_train():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        data = json.load(f)
    p90 = [s for s in data if s["stage_id"] == "P90_PACKAGING"][0]
    assert p90["can_train"] == False
    assert p90["can_tune"] == False

def test_p98_cannot_train():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        data = json.load(f)
    p98 = [s for s in data if s["stage_id"] == "P98_MONITORING"][0]
    assert p98["can_train"] == False

def test_p99_no_side_effects():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        data = json.load(f)
    p99 = [s for s in data if s["stage_id"] == "P99_RUN_SUMMARY"][0]
    assert p99["scientific_side_effects"] == False
