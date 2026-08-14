import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_all_required_runtime_and_demo_artifacts_exist():
    inventory = json.loads((REPORT / "feature_3_9_runtime_artifact_inventory.json").read_text(encoding="utf-8"))
    assert inventory["required_artifact_count"] == 22
    assert inventory["missing_required_artifact_count"] == 0
    for item in inventory["artifacts"]:
        assert item["exists"] is True, item["logical_name"]
        assert (ROOT / item["relative_path"]).is_file(), item["logical_name"]
