"""
Pipeline loader singleton — Feature 3.2 FastAPI Backend.

Applies 4 runtime patches before joblib.load to resolve the EPIC 2 pickle
environment mismatch (transformers module conflict, __main__.to_string,
sys.path, fit interception).
"""
from __future__ import annotations

import json
import logging
import sys
import types
import importlib.util
from pathlib import Path
from datetime import datetime, timezone

import joblib


logger = logging.getLogger(__name__)


# ── Runtime patches ─────────────────────────────────────────────────────────────

def _safe_to_string(x):
    """Per-column string converter — preserves 2D array shape."""
    if hasattr(x, "iloc"):
        return x.astype(str).to_numpy()
    return x


def _apply_runtime_patches(transformers_path: Path, artifacts_path: Path) -> list[str]:
    """Apply all patches needed to deserialize full_inference_pipeline.joblib."""
    patches: list[str] = []

    # Patch 1: EPIC2 transformers into sys.modules["transformers"]
    if transformers_path.exists():
        spec = importlib.util.spec_from_file_location("transformers", str(transformers_path))
        fe_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fe_module)
        sys.modules["transformers"] = fe_module
        patches.append("transformers -> EPIC2.FeatureEngineeringTransformer")

    # Patch 2: __main__.to_string stub
    _main_mod = types.ModuleType("__main__")
    _main_mod.to_string = _safe_to_string
    sys.modules["__main__"] = _main_mod
    patches.append("__main__.to_string -> safe per-column converter")

    # Patch 3: sys.path for module resolution
    runtime_dir = Path(artifacts_path) / "runtime"
    pkg_dir = Path(artifacts_path)
    if runtime_dir.exists() and str(runtime_dir) not in sys.path:
        sys.path.insert(0, str(runtime_dir))
    if str(pkg_dir) not in sys.path:
        sys.path.insert(0, str(pkg_dir))
    patches.append(f"sys.path: {runtime_dir.name}, {pkg_dir.name}")

    return patches


def _patch_pipeline_to_str(pipeline) -> None:
    """Post-load: fix the broken to_str FunctionTransformer.func."""
    try:
        cat = pipeline.champion_pipeline.named_steps["prep"].named_transformers_["cat"]
        cat.named_steps["to_str"].func = _safe_to_string
    except Exception:
        pass  # Non-fatal if pipeline structure differs


# ── PipelineLoader ──────────────────────────────────────────────────────────────

class PipelineLoader:
    """
    Singleton pipeline loader.

    Loads the HitRadarInferencePipeline on first access (lazy) or at startup (eager).
    Caches schemas, metadata, and selected feature names.
    """

    _instance: "PipelineLoader | None" = None

    def __init__(
        self,
        pipeline_path: Path,
        epic2_fe_transformers_path: Path,
        artifacts_path: Path,
    ):
        self.pipeline_path = Path(pipeline_path)
        self.epic2_fe_transformers_path = Path(epic2_fe_transformers_path)
        self.artifacts_path = Path(artifacts_path)
        self._pipeline = None
        self._schemas: dict | None = None
        self._metadata: dict | None = None
        self._selected_features: list[str] | None = None

    @classmethod
    def get_instance(cls) -> "PipelineLoader | None":
        return cls._instance

    @classmethod
    def set_instance(cls, loader: "PipelineLoader") -> None:
        cls._instance = loader

    @classmethod
    def clear_instance(cls) -> None:
        cls._instance = None

    # ── Pipeline ──────────────────────────────────────────────────────────────

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = self._load_pipeline()
        return self._pipeline

    def _load_pipeline(self):
        logger.info("Loading full_inference_pipeline.joblib ...")
        patches = _apply_runtime_patches(
            self.epic2_fe_transformers_path,
            self.artifacts_path,
        )
        for p in patches:
            logger.info(f"  [PATCH] {p}")

        pipe = joblib.load(self.pipeline_path)
        _patch_pipeline_to_str(pipe)
        logger.info("Pipeline loaded successfully.")
        return pipe

    def is_loaded(self) -> bool:
        return self._pipeline is not None

    # ── Schemas ──────────────────────────────────────────────────────────────

    def get_input_schema(self) -> dict:
        if self._schemas is None:
            self._load_schemas()
        return self._schemas["input_schema"]  # type: ignore[return-value]

    def get_selected_features(self) -> list[str]:
        if self._selected_features is None:
            self._load_schemas()
        return self._selected_features  # type: ignore[return-value]

    def _load_schemas(self) -> None:
        schemas_dir = self.artifacts_path / "schemas"
        schemas: dict = {}
        for fname in ["input_schema", "selected_features"]:
            p = schemas_dir / f"{fname}.json"
            with open(p, encoding="utf-8") as f:
                schemas[fname] = json.load(f)
        sf = schemas["selected_features"]
        self._selected_features = sf.get(
            "features",
            sf.get("feature_names", sf.get("selected", [])),
        )
        self._schemas = schemas

    # ── Metadata ──────────────────────────────────────────────────────────────

    def get_model_info(self) -> dict:
        if self._metadata is None:
            self._load_metadata()
        return self._metadata  # type: ignore[return-value]

    def _load_metadata(self) -> None:
        meta_dir = self.artifacts_path / "metadata"
        meta: dict = {}
        for fname in ["model_version", "data_version", "package_version"]:
            p = meta_dir / f"{fname}.json"
            with open(p, encoding="utf-8") as f:
                meta[fname] = json.load(f)
        self._metadata = meta

    # ── Model info shortcuts ─────────────────────────────────────────────────

    def get_model_id(self) -> str:
        return self.get_model_info().get("model_version", {}).get("model_id", "UNKNOWN")

    def get_package_version(self) -> str:
        return self.get_model_info().get("package_version", {}).get("version", "1.0.0")

    # ── Timestamps ───────────────────────────────────────────────────────────

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
