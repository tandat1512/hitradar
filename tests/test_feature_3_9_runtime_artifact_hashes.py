import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_runtime_inventory_hashes_match_current_files_and_accepted_evidence():
    inventory = json.loads((REPORT / "feature_3_9_runtime_artifact_inventory.json").read_text(encoding="utf-8"))
    assert inventory["artifact_hash_mismatch_count"] == 0
    for item in inventory["artifacts"]:
        data = (ROOT / item["relative_path"]).read_bytes()
        assert len(data) == item["bytes"], item["logical_name"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"], item["logical_name"]
        assert item["sha256"] == item["expected_sha256"], item["logical_name"]
