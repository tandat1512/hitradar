"""
Pipeline loader — EPIC 3 FastAPI Backend
Singleton that loads and manages the HitRadarInferencePipeline.
"""
from __future__ import annotations

import json
import joblib
import logging
from pathlib import Path
from datetime import datetime, timezone

from runtime_patches import apply_runtime_patches, patch_pipeline_to_str

logger = logging.getLogger(__name__)


class PipelineLoader:
    """Loads and caches the HitRadarInferencePipeline at startup."""

    def __init__(self, artifacts_path: str, epic2_fe_path: str):
        self.artifacts_path = Path(artifacts_path)
        self.epic2_fe_path = Path(epic2_fe_path)
        self._pipeline = None
        self._schemas: dict | None = None
        self._metadata: dict | None = None
        self._selected_features: list | None = None

    # ── Pipeline ───────────────────────────────────────────────────────────────

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = self._load_pipeline()
        return self._pipeline

    def _load_pipeline(self):
        logger.info("Loading full_inference_pipeline.joblib ...")
        patches = apply_runtime_patches(
            transformers_path=self.epic2_fe_path,
            artifacts_path=str(self.artifacts_path),
        )
        for p in patches:
            logger.info(f"  [PATCH] {p}")

        pipeline_path = self.artifacts_path / "pipeline" / "full_inference_pipeline.joblib"
        pipe = joblib.load(pipeline_path)
        patch_pipeline_to_str(pipe)
        logger.info("Pipeline loaded successfully.")
        return pipe

    def is_loaded(self) -> bool:
        return self._pipeline is not None

    # ── Schemas ─────────────────────────────────────────────────────────────────

    def get_input_schema(self) -> dict:
        if self._schemas is None:
            self._schemas = self._load_schemas()
        return self._schemas["input_schema"]

    def get_selected_features(self) -> list:
        if self._selected_features is None:
            self._load_schemas()
        return self._selected_features  # type: ignore

    def _load_schemas(self):
        schemas_dir = self.artifacts_path / "schemas"
        schemas = {}
        for fname in ["input_schema", "selected_features"]:
            p = schemas_dir / f"{fname}.json"
            with open(p, encoding="utf-8") as f:
                schemas[fname] = json.load(f)
        # selected_features.json uses key "features", not "feature_names"
        sf = schemas["selected_features"]
        self._selected_features = sf.get(
            "features",
            sf.get("feature_names", sf.get("selected", [])),
        )
        return schemas

    # ── Metadata ────────────────────────────────────────────────────────────────

    def get_model_info(self) -> dict:
        if self._metadata is None:
            self._metadata = self._load_metadata()
        return self._metadata

    def _load_metadata(self) -> dict:
        meta_dir = self.artifacts_path / "metadata"
        meta = {}
        for fname in ["model_version", "data_version", "package_version"]:
            p = meta_dir / f"{fname}.json"
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
                meta[fname] = data
        return meta

    # ── Timestamps ──────────────────────────────────────────────────────────────

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
