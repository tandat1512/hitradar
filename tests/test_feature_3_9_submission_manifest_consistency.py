import hashlib
from pathlib import Path

from _feature_3_9_phase_2_helpers import ROOT, load


def test_feature_3_9_submission_manifest_consistency():
    package = load("feature_3_9_submission_package_final.json")
    for relative_path, expected_hash in package["hashes"].items():
        path = ROOT / Path(relative_path)
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
    slide = next(item for item in package["files"] if item["role"] == "final_slide_deck")
    assert slide["status"] == "READY"
    assert slide["path"] in package["hashes"]
    assert package["submission_package_ready"] is False
