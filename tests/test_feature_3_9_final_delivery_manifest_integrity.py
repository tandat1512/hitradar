import hashlib
from pathlib import Path

from _feature_3_9_phase_2_helpers import ROOT, load


def test_feature_3_9_final_delivery_manifest_paths_and_hashes_are_current():
    manifest = load("feature_3_9_final_delivery_manifest.json")
    assert manifest["item_count"] == len(manifest["items"])
    for item in manifest["items"]:
        reference = item.get("path_or_reference")
        if not reference:
            assert item["exists"] is False
            assert item["sha256"] is None
            continue
        path = ROOT / Path(reference)
        assert path.is_file() is item["exists"], item["logical_name"]
        if item["exists"]:
            assert path.stat().st_size == item["bytes"], item["logical_name"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["logical_name"]
