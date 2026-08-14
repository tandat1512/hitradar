"""
Runtime Patches — EPIC 3 FastAPI Backend

Three patches required to load full_inference_pipeline.joblib in EPIC 3's Python environment:

1. transformers conflict: EPIC 2 used `from transformers import FeatureEngineeringTransformer`
   but the Hugging Face `transformers` library is installed. We load EPIC 2's custom
   transformers.py into sys.modules["transformers"] before joblib.load.

2. __main__.to_string: Pipeline pickle references a to_string function from the training
   script's __main__ module. The original implementation called str(df) which collapses
   the entire DataFrame to one string — breaking SimpleImputer. We replace it with a
   safe per-column string converter.

3. to_str FunctionTransformer: After loading, the cat sub-pipeline's to_str step holds
   the broken lambda. We patch its .func attribute to use our safe converter.
"""
from __future__ import annotations

import sys
import types
import importlib.util
from pathlib import Path


def _safe_to_string(x):
    """Convert each column to string individually, preserving 2D array shape."""
    if hasattr(x, "iloc"):
        return x.astype(str).to_numpy()
    return x


def apply_runtime_patches(
    transformers_path: Path,
    artifacts_path: Path,
) -> list[str]:
    """
    Apply all runtime patches needed to load the pipeline.
    Returns list of patch names applied.
    """
    patches = []

    # ── Patch 1: transformers module ─────────────────────────────────────────
    if transformers_path.exists():
        spec = importlib.util.spec_from_file_location("transformers", str(transformers_path))
        fe_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fe_module)
        sys.modules["transformers"] = fe_module
        patches.append("transformers -> EPIC2 FeatureEngineeringTransformer")

    # ── Patch 2: __main__.to_string stub ─────────────────────────────────────
    _main_mod = types.ModuleType("__main__")
    _main_mod.to_string = _safe_to_string
    sys.modules["__main__"] = _main_mod
    patches.append("__main__.to_string -> safe per-column converter")

    # ── Patch 3: sys.path for inference_pipeline module resolution ─────────────
    runtime_dir = Path(artifacts_path) / "runtime"
    if runtime_dir.exists() and str(runtime_dir) not in sys.path:
        sys.path.insert(0, str(runtime_dir))
    if str(artifacts_path) not in sys.path:
        sys.path.insert(0, str(artifacts_path))
    patches.append(f"sys.path: {runtime_dir.name}, {Path(artifacts_path).name}")

    return patches


def patch_pipeline_to_str(pipeline) -> None:
    """
    Post-load patch: replace the broken to_str FunctionTransformer.func
    inside the ColumnTransformer cat sub-pipeline.
    """
    try:
        cat = pipeline.champion_pipeline.named_steps["prep"].named_transformers_["cat"]
        cat.named_steps["to_str"].func = _safe_to_string
    except Exception:
        pass  # Non-fatal if structure differs from expected
