"""
Config — EPIC 3 FastAPI Backend
"""
import os
from pathlib import Path

# Base dir: project root (parent of 5.UNG_DUNG/)
BASE_DIR = Path(__file__).parent.parent.parent.resolve()

# Artifacts canonical location (set up by Feature 3.1)
ARTIFACTS_DIR = BASE_DIR / "artifacts" / "epic2"
ARTIFACTS_PATH = os.environ.get("ARTIFACTS_PATH", str(ARTIFACTS_DIR))

# SHAP explainability artifacts (Feature 2.9)
SHAP_DIR = BASE_DIR / "7.ML" / "7.9.explainability"

# Package sub-directories
RUNTIME_DIR = Path(ARTIFACTS_PATH) / "runtime"
SCHEMAS_DIR = Path(ARTIFACTS_PATH) / "schemas"
EXAMPLES_DIR = Path(ARTIFACTS_PATH) / "examples"
METADATA_DIR = Path(ARTIFACTS_PATH) / "metadata"

# EPIC 2 feature engineering transformers (for module patching)
EPIC2_FE_SRC = BASE_DIR / "7.ML" / "7.6.feature_engineering" / "src"
FE_TRANSFORMERS_PATH = EPIC2_FE_SRC / "transformers.py"
