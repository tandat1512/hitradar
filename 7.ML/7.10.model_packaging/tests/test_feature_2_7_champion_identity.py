import os, json
def test_champion_identity():
    path = os.path.join(r"<PROJECT_ROOT>/7.ML/7.10.model_packaging", "validation", "feature_2_7_champion_identity_validation.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["is_valid"] == True
