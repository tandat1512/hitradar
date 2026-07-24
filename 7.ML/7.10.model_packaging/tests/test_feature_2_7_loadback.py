import os, json
def test_loadback():
    path = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "packaged_artifact_load_validation.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["best_model_load_success"] == True
    assert data["prep_load_success"] == True
    assert data["fitted_state_preserved"] == True
