import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_discovery_file_exists():
    assert (F29 / "registries" / "feature_2_9_epic2_component_discovery.json").exists()

def test_discovery_has_components():
    with open(F29 / "registries" / "feature_2_9_epic2_component_discovery.json", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) > 30, f"Expected 30+ components, got {len(data)}"

def test_no_verified_for_nonexistent():
    with open(F29 / "registries" / "feature_2_9_epic2_component_discovery.json", encoding="utf-8") as f:
        data = json.load(f)
    for c in data:
        if not c["exists"]:
            assert c["verification_status"] != "VERIFIED", f"Non-existent {c['logical_component']} marked VERIFIED"
