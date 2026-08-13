import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_assignment_template_has_all_roles_but_no_false_assignment():
    doc = (REPORT / "DEFENSE_PRESENTER_ASSIGNMENT.md").read_text(encoding="utf-8")
    for section in ("Introduction", "Dataset", "Model", "SHAP", "Architecture", "Live demo operator", "Limitations", "Conclusion"):
        assert section in doc
    assert "PRIMARY_DEMO_OPERATOR:** `UNASSIGNED`" in doc
    assert "BACKUP_DEMO_OPERATOR:** `UNASSIGNED`" in doc
    assert doc.count("UNASSIGNED") >= 20
    gate = json.loads((REPORT / "feature_3_8_phase_4_gate.json").read_text(encoding="utf-8"))
    assert gate["demo_operator_assigned"] is False
    assert gate["qa_ownership_assigned"] is False
    assert gate["status"] == "WAITING_FOR_HUMAN_ACTION"
