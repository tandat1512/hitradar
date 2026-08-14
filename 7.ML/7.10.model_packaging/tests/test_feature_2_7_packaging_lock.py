import os, json
def test_packaging_lock():
    path = os.path.join(r"<PROJECT_ROOT>/7.ML/7.10.model_packaging", "manifests", "champion_packaging_lock.json")
    assert os.path.exists(path)
    data = json.load(open(path, 'r', encoding='utf-8'))
    assert data["training_allowed"] == False
    assert data["tuning_allowed"] == False
