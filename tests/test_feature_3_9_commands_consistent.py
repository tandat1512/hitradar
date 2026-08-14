from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_commands_consistent():
    audit = load("feature_3_9_final_command_doc_audit.json")
    assert audit["command_doc_mismatch_count"] == 0
    assert audit["port_doc_mismatch_count"] == 0
