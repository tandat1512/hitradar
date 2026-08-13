from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_document_audits_record_method_and_source_hashes():
    for name in [
        "feature_3_9_final_model_doc_audit.json",
        "feature_3_9_final_api_doc_audit.json",
        "feature_3_9_final_command_doc_audit.json",
        "feature_3_9_final_claim_audit.json",
    ]:
        audit = load(name)
        assert audit["audit_method"]
        assert audit["source_sha256"]


def test_feature_3_9_ui_audit_is_tied_to_current_source():
    audit = load("feature_3_9_final_ui_doc_audit.json")
    assert audit["audit_method"]
    assert audit["source_sha256"]
    assert audit["canonical_range_present"] is True
