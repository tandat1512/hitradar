import os
def test_requirements():
    assert os.path.exists(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","requirements-runtime.txt"))
    assert os.path.exists(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","requirements-lock.txt"))
    with open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","requirements-runtime.txt")) as f:
        content = f.read()
    assert "numpy" in content
    assert "pandas" in content
    assert "xgboost" in content
