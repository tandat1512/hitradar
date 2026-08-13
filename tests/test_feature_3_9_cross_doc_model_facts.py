from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_cross_doc_model_facts():
    audit = load("feature_3_9_final_model_doc_audit.json")
    assert audit["wrong_model_name_count"] == 0
    assert audit["wrong_model_version_count"] == 0
    assert audit["feature_count_mismatch_count"] == 0
    assert audit["target_mismatch_count"] == 0
