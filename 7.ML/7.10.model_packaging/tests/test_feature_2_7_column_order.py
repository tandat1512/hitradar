import os, json
def test_column_order():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "input_column_order_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["is_invariant"]
    assert d["difference"] < 1e-6
