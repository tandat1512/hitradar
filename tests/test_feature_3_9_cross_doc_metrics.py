from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_cross_doc_metrics():
    audit = load("feature_3_9_final_model_doc_audit.json")
    assert audit["metric_mismatch_count"] == 0
    assert audit["accuracy_mislabel_count"] == 0
