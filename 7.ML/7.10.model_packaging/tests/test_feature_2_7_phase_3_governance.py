import os, json
def test_phase_3_governance():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","checkpoints","feature_2_7_phase_3_checkpoint.json"),encoding="utf-8"))
    assert d["phase_status"] in ("PASS","PASS_WITH_WARNINGS")
    assert d["next_phase"] == "MAY_BEGIN"
    assert not d["training_executed"]
    assert not d["tuning_executed"]
    assert not d["refit_executed"]
    assert d["happy_path_tests_complete"]
    assert d["prediction_deterministic"]
    assert d["serialization_roundtrip_valid"]
    assert d["no_refit_during_inference"]
    assert d["example_output_generated_by_pipeline"]
    assert d["artifact_manifest_valid"]
