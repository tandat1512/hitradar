import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_dependency_specifications_exist_and_have_no_local_file_references():
    audit = json.loads((REPORT / "feature_3_9_dependency_final_audit.json").read_text(encoding="utf-8"))
    assert audit["dependency_spec_present"] is True
    assert audit["critical_package_coverage_complete"] is True
    assert audit["no_local_file_dev_paths"] is True
    for item in audit["specifications"]:
        assert (ROOT / item["path"]).is_file()
        assert item["local_file_reference_count"] == 0
