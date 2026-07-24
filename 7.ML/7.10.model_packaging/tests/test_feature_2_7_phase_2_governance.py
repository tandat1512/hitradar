import os, json
def test_phase_2_governance():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "checkpoints", "feature_2_7_phase_2_checkpoint.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["phase_status"] in ("PASS", "PASS_WITH_WARNINGS")
    assert d["next_phase"] == "MAY_BEGIN"
    assert d["champion_hash_unchanged"]
    assert not d["training_executed"]
    assert not d["tuning_executed"]
    assert not d["preprocessing_refit"]
