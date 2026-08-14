"""Test 1: Handoff Discovery
Verify handoff_to_epic3.md is found (or functional substitute is recorded).
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
CANONICAL_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
HDISCOV_FILE = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "inventories" / "feature_3_1_handoff_discovery.json"

def test_handoff_discovery_file_exists():
    assert HDISCOV_FILE.exists(), f"Handoff discovery file not found: {HDISCOV_FILE}"

def test_handoff_discovery_content():
    with open(HDISCOV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "BLOCKED"
    assert data["handoff_doc_target"] == "handoff_to_epic3.md"
    assert "handoff_to_epic3_md_found" in data["search_result"]

def test_handoff_searched_expected_locations():
    with open(HDISCOV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    locations = data["search_result"]["handoff_to_epic3_md_locations_searched"]
    assert isinstance(locations, list)
    assert len(locations) > 0

def test_functional_handoff_substitute_identified():
    with open(HDISCOV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    sr = data["search_result"]
    assert sr["functional_handoff_substitute_found"] == True
    sub = sr["functional_handoff"]
    assert "MODEL_PACKAGE_README.md" in sub.get("path", "")

def test_readme_exists():
    readme = CANONICAL_ROOT / "MODEL_PACKAGE_README.md"
    assert readme.exists(), f"MODEL_PACKAGE_README.md not found at {readme}"

def test_blocker_recorded():
    with open(HDISCOV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    blockers = data.get("blockers", [])
    assert len(blockers) > 0, "Expected at least one blocker for missing handoff document"
