"""Test 8: Requirements Files
Verify all requirements-*.txt files exist and are non-empty.
"""
import pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"

def test_requirements_runtime_exists():
    f = PKG_ROOT / "requirements-runtime.txt"
    assert f.exists()
    assert f.stat().st_size > 0

def test_requirements_explainability_exists():
    f = PKG_ROOT / "requirements-explainability.txt"
    assert f.exists()
    assert f.stat().st_size > 0

def test_requirements_lock_exists():
    f = PKG_ROOT / "requirements-lock.txt"
    assert f.exists()

def test_requirements_runtime_has_fastapi():
    f = PKG_ROOT / "requirements-runtime.txt"
    content = f.read_text(encoding="utf-8").lower()
    # Should contain at least one ML/API framework
    assert any(kw in content for kw in ["fastapi", "uvicorn", "xgboost", "scikit", "joblib", "pandas", "numpy"])

def test_requirements_explainability_has_shap():
    f = PKG_ROOT / "requirements-explainability.txt"
    content = f.read_text(encoding="utf-8").lower()
    assert "shap" in content, "requirements-explainability.txt should mention 'shap'"
