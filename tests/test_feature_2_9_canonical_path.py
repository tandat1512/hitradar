import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_canonical_dir_exists():
    assert F29.exists()

def test_required_subdirs():
    for sd in ["scripts", "configs", "registries", "manifests", "checkpoints", "validation", "logs"]:
        assert (F29 / sd).exists(), f"Missing subdir: {sd}"

def test_canonical_path_validation():
    path = F29 / "validation" / "feature_2_9_canonical_path_validation.json"
    assert path.exists()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"
    assert data["all_subdirs_exist"] == True
