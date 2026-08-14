import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_no_machine_specific_path_is_required_by_supported_runtime():
    audit = json.loads((REPORT / "feature_3_9_artifact_path_validation.json").read_text(encoding="utf-8"))
    assert audit["machine_specific_runtime_path_count"] == 0
    assert audit["blocking_path_count"] == 0
    runtime_entries = [item for item in audit["paths"] if item.get("runtime_required", True)]
    assert all(item["machine_specific"] is False for item in runtime_entries)
