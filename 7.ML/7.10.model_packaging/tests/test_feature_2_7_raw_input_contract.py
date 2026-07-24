import os, json
def test_raw_input_contract():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "raw_input_contract_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["is_valid"]
    assert d["expected_count"] == 18
    assert d["target_excluded"]
    assert d["identifier_excluded"]
