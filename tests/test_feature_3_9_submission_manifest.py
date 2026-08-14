from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_submission_manifest_is_honest_and_classified():
    manifest = load("feature_3_9_submission_package_manifest.json")
    assert manifest["submission_requirement_status"] == "SUBMISSION_REQUIREMENTS_PARTIALLY_UNKNOWN"
    assert manifest["entries"]
    assert all(item["classification"] in {"REQUIRED_BY_KNOWN_REQUIREMENT", "PROJECT_RECOMMENDED", "OPTIONAL", "NOT_FOR_SUBMISSION"} for item in manifest["entries"])
    slide = next(item for item in manifest["entries"] if item["role"] == "final_slide_deck")
    assert slide["status"] == "READY"
    assert slide["exists"] is True
    assert slide["bytes"] > 0
