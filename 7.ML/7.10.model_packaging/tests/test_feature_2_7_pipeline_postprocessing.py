import os, json
def test_postprocessing():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","inference_postprocessing_validation.json"),encoding="utf-8"))
    assert d["is_valid"]
    assert d["clipped_match"]
    assert d["display_match"]
    assert d["clipped_in_range"]
