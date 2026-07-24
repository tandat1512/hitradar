import os, json
def test_full_pipeline_prediction():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "full_pipeline_load_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    pred = d["sample_prediction"]
    assert pred["status"] == "SUCCESS"
    assert isinstance(pred["prediction_raw"], (int, float))
    assert 0 <= pred["prediction_clipped"] <= 100
