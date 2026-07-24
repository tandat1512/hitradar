import os, json
def test_examples():
    d1 = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","example_input_validation.json"),encoding="utf-8"))
    assert d1["is_valid"]
    d2 = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","example_roundtrip_validation.json"),encoding="utf-8"))
    assert d2["is_valid"]
    assert d2["raw_match"]
    assert d2["display_match"]
    assert os.path.exists(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","examples","example_output.json"))
