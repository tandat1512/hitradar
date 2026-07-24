import os, json
def test_no_refit():
    path = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "feature_2_7_no_refit_validation.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["is_valid"] == True
    assert data["fit_call_count"] == 0
    assert data["fit_transform_call_count"] == 0
