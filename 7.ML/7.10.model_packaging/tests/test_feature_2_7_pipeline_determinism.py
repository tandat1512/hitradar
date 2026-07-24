import os, json
def test_determinism():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","inference_determinism_validation.json"),encoding="utf-8"))
    assert d["is_deterministic"]
    assert d["std"] < 1e-10
