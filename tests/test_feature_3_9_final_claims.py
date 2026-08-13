from _feature_3_9_phase_2_helpers import load


def test_feature_3_9_final_claims():
    audit = load("feature_3_9_final_claim_audit.json")
    assert audit["unsupported_claim_count"] == 0
