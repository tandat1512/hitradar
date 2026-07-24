import os, json
def test_feature_names():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "schemas", "feature_names.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["model_matrix_width"] == 49
    assert d["feature_name_count"] == d["model_matrix_width"]
    assert d["order_locked"]
