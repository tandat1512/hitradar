import os, json
def test_dimensions():
    path = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "manifests", "feature_2_7_dimension_contract.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["api_input_contract_field_count"] == 18
    assert data["dimensions_consistent"] == True
