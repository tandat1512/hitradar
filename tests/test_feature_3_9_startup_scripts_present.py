import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_all_canonical_startup_scripts_are_present_and_portable_by_path():
    audit = json.loads((REPORT / "feature_3_9_startup_script_final_audit.json").read_text(encoding="utf-8"))
    assert {item["logical_name"] for item in audit["scripts"]} == {"run_backend", "run_frontend", "run_all"}
    for item in audit["scripts"]:
        assert item["exists"] is True
        assert item["absolute_dev_path_count"] == 0
        assert (ROOT / item["path"]).is_file()
