import os, json
def test_artifact_manifest():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","artifact_manifest_validation.json"),encoding="utf-8"))
    assert d["is_valid"]
    assert d["artifact_count"] >= 15
