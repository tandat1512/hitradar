import os, json
def test_invalid_inputs():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","invalid_input_test_results.json"),encoding="utf-8"))
    assert d["missing_field_rejected"]
    assert d["inf_rejected"]
    assert d["neg_inf_rejected"]
    assert d["wrong_type_rejected"]
    assert d["duplicate_col_rejected"]
