import os, json
def test_phase_1_governance():
    path = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "checkpoints", "feature_2_7_phase_1_checkpoint.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["phase_status"] in ["PASS", "PASS_WITH_WARNINGS"]
    assert data["next_phase"] == "MAY_BEGIN"
