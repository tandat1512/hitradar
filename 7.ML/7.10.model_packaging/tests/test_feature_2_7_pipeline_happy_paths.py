import os, json
def test_happy_paths():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","happy_path_test_results.json"),encoding="utf-8"))
    assert d["dict_single"]
    assert d["series"]
    assert d["df_single"]
    assert d["df_batch"]
    assert d["order_invariant"]
