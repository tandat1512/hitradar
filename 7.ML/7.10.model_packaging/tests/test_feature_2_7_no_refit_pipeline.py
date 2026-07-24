import os, json
def test_no_refit_pipeline():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "full_pipeline_no_refit_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["is_valid"]
    assert d["fit_call_count"] == 0
    assert d["fit_transform_call_count"] == 0
