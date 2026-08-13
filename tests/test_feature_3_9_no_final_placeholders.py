from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_no_final_placeholders():
    audit = load("feature_3_9_placeholder_audit.json")
    assert audit["unresolved_placeholder_count"] == 0, audit["blocking_findings"]
