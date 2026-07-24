import os, json
def test_selected_features():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "schemas", "selected_features.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["feature_set_id"] == "FS23-SELECTED"
    assert d["feature_count"] == 31
    assert d["feature_count"] == len(d["features"])
    assert d["feature_order_locked"]
