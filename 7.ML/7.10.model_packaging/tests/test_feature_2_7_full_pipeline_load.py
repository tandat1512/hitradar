import os, json
def test_full_pipeline_load():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "full_pipeline_load_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["load_success"]
    assert d["prediction_success"]
