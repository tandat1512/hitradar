from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_final_report_exists():
    audit = load("feature_3_9_final_report_resolution.json")
    assert audit["final_report_resolved"] is True
    assert audit["ambiguity"] is False
