import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_what_if_presenter_line_is_noncausal_and_direction_neutral():
    registry = json.loads((REPORT / "feature_3_8_demo_step_registry.json").read_text(encoding="utf-8"))
    line = next(step["presenter_line"] for step in registry["steps"] if step["step_id"] == "WHAT_IF").lower()
    assert "hai model predictions" in line
    assert "không phải tác động thực tế" in line
    assert "sẽ tăng" not in line
    assert "sẽ giảm" not in line
