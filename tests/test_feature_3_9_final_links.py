from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_final_links():
    audit = load("feature_3_9_final_link_audit.json")
    assert audit["broken_links"] == 0
    assert audit["missing_assets"] == 0
