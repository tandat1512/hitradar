import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_only_evidenced_contributors_are_named_and_roles_unconfirmed():
    validation = json.loads((REPORT / "feature_3_8_team_member_validation.json").read_text(encoding="utf-8"))
    contributors = validation["verified_project_contributors"]
    assert {item["name"] for item in contributors} == {"Minh", "Đạt"}
    assert all(item["evidence"] for item in contributors)
    assert all(item["presentation_role_confirmed"] is False for item in contributors)
    assert validation["authoritative_full_team_roster_found"] is False
    assert validation["status"] == "HUMAN_ROSTER_CONFIRMATION_REQUIRED"
    assignment = (REPORT / "DEFENSE_PRESENTER_ASSIGNMENT.md").read_text(encoding="utf-8")
    assert "consent" in assignment.lower()
    assert "Human sign-off" in assignment
