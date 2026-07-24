import os, json
def test_output_schema():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "schemas", "output_schema.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["schema_id"] == "HITRADAR-PREDICTION-OUTPUT-V1"
    names = [f["name"] for f in d["fields"]]
    assert "prediction_raw" in names
    assert "prediction_clipped" in names
    assert "prediction_display" in names
