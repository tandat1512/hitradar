import os, json
def test_input_validation():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "schemas", "input_schema.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["field_count"] == 18
    assert len(d["fields"]) == 18
    names = [f["name"] for f in d["fields"]]
    assert "target_popularity" not in names
    assert "track_id" not in names
