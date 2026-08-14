from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_release_record_does_not_invent_release_sha():
    record = load("feature_3_9_release_record.json")
    commit = load("feature_3_9_final_commit_record.json")
    assert record["release_mode"] == "FINAL_COMMIT_ONLY"
    assert commit["commit_executed"] is False
    assert commit["new_commit_sha"] is None
    assert record["final_commit_sha"] is None
    assert record["release_record_complete"] is False
