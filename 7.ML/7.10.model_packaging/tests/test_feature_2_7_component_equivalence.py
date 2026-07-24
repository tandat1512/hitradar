import os, json
def test_component_equivalence():
    path = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "packaged_component_equivalence_validation.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["is_equivalent"] == True
