import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_explain_presenter_line_is_noncausal():
    registry = json.loads((REPORT / "feature_3_8_demo_step_registry.json").read_text(encoding="utf-8"))
    line = next(step["presenter_line"] for step in registry["steps"] if step["step_id"] == "EXPLAIN").lower()
    assert "đóng góp" in line
    assert "model behavior" in line
    assert "không chứng minh quan hệ nhân quả" in line
    assert "nguyên nhân bài hát nổi tiếng" not in line
