import os, json
def test_no_refit():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","inference_no_refit_results.json"),encoding="utf-8"))
    assert d["is_valid"]
    assert d["fit_call_count"] == 0
    assert d["fit_transform_call_count"] == 0
