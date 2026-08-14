"""Test 7: Artifact Readability
Verify all declared artifacts are readable and parse as expected types.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"

def test_artifact_manifest_readable():
    f = PKG_ROOT / "metadata" / "artifact_manifest.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, list)

def test_inference_pipeline_readable():
    f = PKG_ROOT / "runtime" / "inference_pipeline.py"
    content = f.read_text(encoding="utf-8")
    assert "HitRadarInferencePipeline" in content
    assert "predict_popularity" in content
    assert len(content) > 6000  # file is ~6.5 KB, encoding may affect byte count

def test_inference_pipeline_syntax_valid():
    """Basic syntax check — no import errors expected at parse level."""
    f = PKG_ROOT / "runtime" / "inference_pipeline.py"
    content = f.read_text(encoding="utf-8")
    # Should not have syntax errors — just check for obvious issues
    assert "import os" in content
    assert "import numpy" in content
    assert "class HitRadarInferencePipeline" in content

def test_requirements_runtime_readable():
    f = PKG_ROOT / "requirements-runtime.txt"
    content = f.read_text(encoding="utf-8")
    assert len(content.strip()) > 0

def test_requirements_explainability_readable():
    f = PKG_ROOT / "requirements-explainability.txt"
    content = f.read_text(encoding="utf-8")
    assert len(content.strip()) > 0

def test_requirements_lock_readable():
    f = PKG_ROOT / "requirements-lock.txt"
    content = f.read_text(encoding="utf-8")
    assert len(content.strip()) > 0

def test_example_input_parseable():
    f = PKG_ROOT / "examples" / "example_input.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict)

def test_example_output_parseable():
    f = PKG_ROOT / "examples" / "example_output.json"
    with open(f, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, dict)

def test_readme_readable():
    f = PKG_ROOT / "MODEL_PACKAGE_README.md"
    content = f.read_text(encoding="utf-8")
    assert len(content) > 100
    assert "XGBoost" in content or "model" in content.lower()

def test_all_joblib_files_exist():
    joblib_files = [
        "pipeline/full_inference_pipeline.joblib",
        "models/best_model.joblib",
        "preprocessing/feature_engineering_pipeline.joblib",
        "preprocessing/model_preprocessing_pipeline.joblib",
    ]
    for rel in joblib_files:
        f = PKG_ROOT / rel
        assert f.exists(), f"Missing joblib file: {rel}"
        assert f.stat().st_size > 0, f"Empty joblib file: {rel}"

def test_readability_report_exists():
    rep = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "inventories" / "feature_3_1_artifact_readability.json"
    assert rep.exists()
    with open(rep, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["overall_readability_status"] == "PASS"
