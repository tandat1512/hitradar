import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_demo_step_contract_and_order():
    registry = json.loads((REPORT / "feature_3_8_demo_step_registry.json").read_text(encoding="utf-8"))
    assert registry["PRIMARY_OPERATOR"] == "UNASSIGNED"
    required = {
        "step_id", "page", "presenter_line", "operator_action", "input",
        "expected_visible_state", "backend_endpoint", "expected_status",
        "target_duration_seconds", "failure_action", "skip_rule", "evidence_source",
    }
    steps = registry["steps"]
    assert [step["step_id"] for step in steps] == [
        "PRECHECK", "HOME", "PREDICT", "EXPLAIN", "WHAT_IF", "TRENDS",
        "MODEL_INFO_LIMITATIONS", "END",
    ]
    assert all(required <= step.keys() for step in steps)
    assert all(isinstance(step["target_duration_seconds"], int) and step["target_duration_seconds"] > 0 for step in steps)
