from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_api_docs_current():
    audit = load("feature_3_9_final_api_doc_audit.json")
    assert audit["total_mismatch_count"] == 0
