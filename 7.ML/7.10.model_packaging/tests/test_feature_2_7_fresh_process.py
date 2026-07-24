import os, json
def test_fresh_process():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","fresh_process_load_validation.json"),encoding="utf-8"))
    assert d["fresh_load_success"]
    assert d["prediction_success"]
