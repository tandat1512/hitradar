"""
Fingerprint computation for config, code, environment, and artifacts.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .pipeline_types import ArtifactFingerprint
from .atomic_writer import compute_sha256


# ---------------------------------------------------------------------------
# Config Fingerprint
# ---------------------------------------------------------------------------

# Fields that affect scientific output vs just execution behaviour
_SCIENTIFIC_CONFIG_KEYS = frozenset({
    "seed", "learning_rate", "max_depth", "n_estimators",
    "objective", "threshold", "feature_columns", "target_column",
    "validation_metric", "early_stopping_rounds", "preprocessing_params",
})

# Execution-only keys (don't invalidate scientific checkpoints)
_EXECUTION_ONLY_KEYS = frozenset({
    "log_level", "verbose", "dry_run", "max_parallel_stages",
    "subprocess_timeout_seconds", "resume",
})


def _normalize_dict(d: dict) -> dict:
    """Recursively normalize dict: sort keys, convert non-dict values to str."""
    if not isinstance(d, dict):
        return {"_": str(d)}
    result = {}
    for k, v in sorted(d.items()):
        if isinstance(v, dict):
            result[k] = _normalize_dict(v)
        elif isinstance(v, list):
            # Sort list elements that are comparable
            try:
                result[k] = sorted(str(x) for x in v)
            except TypeError:
                result[k] = [str(x) for x in v]
        else:
            result[k] = v
    return result


def _dict_hash(d: dict) -> str:
    """Compute SHA-256 of a normalized dict."""
    normalized = _normalize_dict(d)
    serialized = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_config_fingerprints(config: dict) -> dict:
    """
    Compute three config hashes:
    - full_config_hash: all fields
    - scientific_config_hash: only scientific-relevant fields
    - execution_config_hash: only execution-relevant fields
    """
    full = config.get("pipeline", {}) or {}
    perms = config.get("permissions", {}) or {}
    exec_cfg = config.get("execution", {}) or {}

    # Full hash
    full_hash = _dict_hash(config)

    # Scientific config: merge pipeline + permissions
    scientific_data = {**full, **perms}
    scientific_hash = _dict_hash(scientific_data)

    # Execution hash: only execution-relevant fields
    execution_data = {k: v for k, v in exec_cfg.items()
                     if k not in _EXECUTION_ONLY_KEYS}
    execution_data["fail_fast"] = full.get("fail_fast", True)
    execution_data["mode"] = full.get("mode", "validate")
    execution_hash = _dict_hash(execution_data)

    return {
        "full_config_hash": full_hash,
        "scientific_config_hash": scientific_hash,
        "execution_config_hash": execution_hash,
        "config_fields": list(config.keys()),
        "scientific_fields": list(scientific_data.keys()),
    }


# ---------------------------------------------------------------------------
# Code Fingerprint
# ---------------------------------------------------------------------------

def compute_code_fingerprint(
    git_commit: str,
    working_tree_dirty: bool,
    stage_adapter_module_path: Optional[str] = None,
    source_script_path: Optional[str] = None,
    registry_path: Optional[str] = None,
    mode_contract_path: Optional[str] = None,
) -> dict:
    """
    Compute code fingerprint for a stage run.
    Includes Git metadata + hashes of key implementation files.
    """
    fingerprint = {
        "git_commit": git_commit or "unknown",
        "working_tree_dirty": working_tree_dirty,
        "stage_adapter_module_hash": None,
        "source_script_hash": None,
        "registry_hash": None,
        "mode_contract_hash": None,
    }

    def _file_hash(path: str) -> Optional[str]:
        if path and os.path.exists(path):
            return compute_sha256(path)
        return None

    if stage_adapter_module_path:
        fingerprint["stage_adapter_module_hash"] = _file_hash(stage_adapter_module_path)
    if source_script_path:
        fingerprint["source_script_hash"] = _file_hash(source_script_path)
    if registry_path:
        fingerprint["registry_hash"] = _file_hash(registry_path)
    if mode_contract_path:
        fingerprint["mode_contract_hash"] = _file_hash(mode_contract_path)

    return fingerprint


# ---------------------------------------------------------------------------
# Environment Fingerprint
# ---------------------------------------------------------------------------

def compute_environment_fingerprint() -> dict:
    """
    Capture environment that affects ML reproducibility.
    """
    env = {
        "python_version": sys.version,
        "python_major": sys.version_info.major,
        "python_minor": sys.version_info.minor,
        "platform": sys.platform,
        "key_dependencies": _get_key_dependency_versions(),
    }

    # Check for requirements lock file
    req_lock = os.environ.get("HOMEDRIVE", "") + os.environ.get("HOMEPATH", "")
    # We don't include HOMEDRIVE/HOMEPATH in fingerprint — just the deps

    return env


def _get_key_dependency_versions() -> dict:
    """Get versions of key ML dependencies."""
    deps = {}
    for name, import_name in [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("sklearn", "sklearn"),
        ("xgboost", "xgboost"),
        ("shap", "shap"),
        ("joblib", "joblib"),
        ("yaml", "yaml"),
    ]:
        try:
            mod = __import__(import_name)
            ver = getattr(mod, "__version__", "unknown")
            deps[name] = ver
        except ImportError:
            deps[name] = None
    return deps


# ---------------------------------------------------------------------------
# Artifact Fingerprint (convenience)
# ---------------------------------------------------------------------------

def fingerprint_file(path: str, producer_stage: Optional[str] = None) -> ArtifactFingerprint:
    """Fingerprint a single file."""
    if not os.path.exists(path):
        return ArtifactFingerprint(
            path=path,
            bytes=0,
            sha256="",
            producer_stage=producer_stage,
            required=True,
        )
    size = os.path.getsize(path)
    sha = compute_sha256(path)
    mtime = os.path.getmtime(path)
    return ArtifactFingerprint(
        path=path,
        bytes=size,
        sha256=sha,
        producer_stage=producer_stage,
        required=True,
        mtime=mtime,
    )
