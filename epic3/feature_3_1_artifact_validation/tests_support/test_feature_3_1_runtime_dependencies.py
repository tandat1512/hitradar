"""Test: Runtime Dependencies
Verify all required packages are installed and compatible.
"""
import json, pathlib, importlib, sys

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
DEP_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_runtime_dependency_validation.json"

REQUIRED_FOR_LOAD = ["sklearn", "xgboost", "joblib", "pandas", "numpy"]
REQUIRED_FOR_SHAP = ["shap"]

def test_dependency_validation_file_exists():
    assert DEP_VAL_FILE.exists()

def test_all_required_packages_importable():
    for pkg in REQUIRED_FOR_LOAD + REQUIRED_FOR_SHAP:
        try:
            importlib.import_module(pkg)
        except ImportError:
            assert False, f"Package '{pkg}' not installed"

def test_sklearn_version():
    import sklearn
    ver = tuple(int(x) for x in sklearn.__version__.split(".")[:2])
    assert ver >= (1, 5), f"sklearn version too old: {sklearn.__version__}"

def test_xgboost_importable():
    import xgboost
    assert xgboost.__version__ is not None

def test_joblib_importable():
    import joblib
    assert joblib.__version__ is not None

def test_runtime_patches_applied():
    with open(DEP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    patches = [p["patch"] for p in data.get("runtime_patches_applied", [])]
    assert "transformers module conflict" in patches
    assert "__main__.to_string stub" in patches
    assert "sys.path runtime resolution" in patches

def test_sklearn_version_mismatch_warning():
    """Pipeline was pickled with sklearn 1.9.0 but running 1.8.0 — this should be warned."""
    with open(DEP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    warnings = [w for w in data.get("warnings", [])]
    assert any("SKLEARN_VERSION_MISMATCH" in str(w) for w in warnings)
    assert data["overall_status"] in ["OK", "WARNING"]

def test_can_proceed_true():
    with open(DEP_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["can_proceed"] == True
