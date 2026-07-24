import os, json
def test_preprocessing():
    path = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "manifests", "preprocessing_manifest.json")
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "package", "preprocessing", "model_preprocessing_pipeline.joblib"))
