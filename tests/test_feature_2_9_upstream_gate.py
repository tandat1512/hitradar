import pytest, json
from pathlib import Path

F29 = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation")

def test_upstream_gate_file_exists():
    assert (F29 / "validation" / "feature_2_8_to_feature_2_9_gate_validation.json").exists()

def test_upstream_gate_has_f28_status():
    with open(F29 / "validation" / "feature_2_8_to_feature_2_9_gate_validation.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "feature_2_8_status" in data
    assert "foundation_status" in data
    assert data["foundation_status"] in ["DEVELOPMENT_ALLOWED", "DEVELOPMENT_ALLOWED_WITH_UPSTREAM_WARNING"]
