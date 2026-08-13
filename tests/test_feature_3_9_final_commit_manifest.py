from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_final_commit_manifest_is_explicit_and_safe():
    candidate = load("feature_3_9_final_commit_candidate.json")
    assert candidate["mode"] == "PREPARE_ONLY"
    assert candidate["files"]
    assert candidate["file_count"] == len(candidate["files"])
    assert all("path" in item and "git_status" in item and "include_in_final_commit" in item for item in candidate["files"])
    assert all(not item["include_in_final_commit"] for item in candidate["files"] if item["classification"] in {"SECRET_RISK", "UNKNOWN", "LOCAL_ENVIRONMENT", "TEMPORARY", "GENERATED_IGNORED", "INVALID_DELIVERABLE"})
    assert candidate["final_commit_candidate_valid"] is False
