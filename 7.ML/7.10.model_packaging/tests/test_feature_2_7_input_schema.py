import os, json
def test_input_schema():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "schemas", "input_schema.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["schema_id"] == "HITRADAR-PREDICTION-INPUT-V1"
    for f in d["fields"]:
        assert "name" in f
        assert "data_type" in f
        assert "required" in f
