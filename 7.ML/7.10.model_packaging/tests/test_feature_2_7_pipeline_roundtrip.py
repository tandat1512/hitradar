import os, json
def test_roundtrip():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","inference_roundtrip_results.json"),encoding="utf-8"))
    assert d["is_valid"]
    assert d["difference"] < 1e-10
