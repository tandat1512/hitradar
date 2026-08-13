"""
Core configuration — Feature 3.2 FastAPI Backend.

Resolves paths from this module's location, not from cwd or hardcoded paths.
Project structure (repo root = parent of epic3/):
  epic3/
    feature_3_2/
      backend/              BACKEND_DIR
        app/
          core/
            config.py
  artifacts/epic2/          ARTIFACTS_CANONICAL
  7.ML/.../package/        EPIC2_PACKAGE_ROOT
"""
from __future__ import annotations

import os
from pathlib import Path

# ── Project root ────────────────────────────────────────────────────────────────
# backend/app/core/config.py  →  app/ → backend/ → feature_3_2/ → epic3/ → repo root
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # app/ → backend/
# 3 more parents from backend/ to reach repo root:
#   feature_3_2/ → epic3/ → DUAN1 github/
_REPO_ROOT   = _BACKEND_DIR.parent.parent.parent

# ── Application ────────────────────────────────────────────────────────────────
APP_NAME = "HitRadar Pro API"
APP_VERSION = "1.0.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ── Server ────────────────────────────────────────────────────────────────────
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ── API ───────────────────────────────────────────────────────────────────────
API_PREFIX = os.getenv("API_PREFIX", "")
MAX_REQUEST_SIZE_MB = int(os.getenv("MAX_REQUEST_SIZE_MB", "1"))

# ── Artifacts ─────────────────────────────────────────────────────────────────
# Primary: artifacts/epic2/ at repo root (Feature 3.1 canonical)
_ARTIFACTS_DEFAULT = _REPO_ROOT / "artifacts" / "epic2"
ARTIFACTS_PATH: Path = Path(os.getenv("ARTIFACTS_PATH", str(_ARTIFACTS_DEFAULT)))

# EPIC2 model package root (for runtime patches — EPIC 2 source transformers)
EPIC2_PACKAGE_ROOT: Path = _REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
EPIC2_FE_TRANSFORMERS: Path = (
    _REPO_ROOT / "7.ML" / "7.6.feature_engineering" / "src" / "transformers.py"
)

# ── Artifact sub-paths ─────────────────────────────────────────────────────────
def _resolve_artifact(*parts: str) -> Path:
    """Resolve artifact sub-path, resolving traversal before returning."""
    resolved = ARTIFACTS_PATH.joinpath(*parts).resolve()
    # Basic traversal guard: resolved path must be under ARTIFACTS_PATH
    try:
        resolved.relative_to(ARTIFACTS_PATH.resolve())
    except ValueError:
        raise ValueError(
            f"Path traversal detected: {resolved} is not under {ARTIFACTS_PATH}"
        )
    return resolved

PIPELINE_PATH = _resolve_artifact("pipeline", "full_inference_pipeline.joblib")
SCHEMAS_DIR = _resolve_artifact("schemas")
EXAMPLES_DIR = _resolve_artifact("examples")
METADATA_DIR = _resolve_artifact("metadata")
RUNTIME_DIR = _resolve_artifact("runtime")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Default origins for local dev (Streamlit frontend).
# Override via ALLOWED_ORIGINS env var (comma-separated).
_DEFAULT_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:3000",
]
_ALLOWED_ORIGINS_ENV = os.getenv("CORS_ALLOWED_ORIGINS", "")
if _ALLOWED_ORIGINS_ENV:
    ALLOWED_ORIGINS = [o.strip() for o in _ALLOWED_ORIGINS_ENV.split(",") if o.strip()]
else:
    ALLOWED_ORIGINS = _DEFAULT_ORIGINS  # NOT "*" — safe for credentials

ALLOWED_METHODS = ["GET", "POST"]
ALLOWED_HEADERS = [
    "Accept",
    "Accept-Language",
    "Authorization",
    "Content-Type",
    "X-Request-ID",
]
# allow_credentials must be False when allow_origins contains "*"
# With specific origins (localhost/127.0.0.1) this is safe.
ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() in ("true", "1", "yes")

# ── Runtime ───────────────────────────────────────────────────────────────────
MODEL_LOAD_STRATEGY = os.getenv("MODEL_LOAD_STRATEGY", "eager")  # eager | lazy
FAIL_STARTUP_IF_MODEL_UNAVAILABLE = os.getenv(
    "FAIL_STARTUP_IF_MODEL_UNAVAILABLE", "false"
).lower() in ("true", "1", "yes")
EXPLANATION_ENABLED = True
WHATIF_ENABLED = True

# ── Summary (for tests) ───────────────────────────────────────────────────────
REPO_ROOT_STR = str(_REPO_ROOT)
BACKEND_DIR_STR = str(_BACKEND_DIR)
