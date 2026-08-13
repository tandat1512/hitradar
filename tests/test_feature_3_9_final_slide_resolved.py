from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_final_slide_resolved():
    audit = load("feature_3_9_final_slide_resolution.json")
    assert audit["final_slide_resolved"] is True, audit["blocker"]
