from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_no_secret_in_commit_candidate():
    candidate = load("feature_3_9_final_commit_candidate.json")
    assert candidate["phase_1_tracked_secret_risk_count"] == 0
    assert candidate["phase_1_untracked_secret_risk_count"] == 0
    assert not [item for item in candidate["files"] if item["classification"] == "SECRET_RISK" and item["include_in_final_commit"]]
