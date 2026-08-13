from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_release_submission_consistency_is_not_falsely_passed():
    audit = load("feature_3_9_release_submission_consistency.json")
    gate = load("feature_3_9_phase_3_gate.json")
    assert audit["release_commit_exists"] is False
    assert audit["release_submission_consistent"] is False
    assert gate["remote_commit_verified"] is False
    assert gate["submission_confirmed"] is False
    assert gate["git_write_authorized"] is False
