import os, json
def test_feature_mapping():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "schemas", "feature_mapping.json")
    d = json.load(open(p, encoding="utf-8"))
    assert len(d) == 49
    for m in d:
        assert m["mapping_status"] == "CONFIRMED"
