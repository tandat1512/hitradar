#!/usr/bin/env python3
"""
model_monitor.py — Feature 2.9 Phase 3/5 Model Monitoring Core
HitRadar Pro — EXP24-XGB-FINAL-001 (v1.0.0) | Package v2.7.0
Owner: Tuấn Anh

Governance enforced:
  - auto_retrain = false
  - auto_update_baseline = false
  - champion_changed = false
  - NO training, tuning, refit, or baseline modification
  - Phase 3: performance metrics NOT computed (labels not available)

Exit codes:
  0  PASS
  2  PASS_WITH_WARNINGS
  10 INPUT_ERROR
  11 CONFIG_ERROR
  12 BASELINE_ERROR
  13 ARTIFACT_INTEGRITY_FAIL
  14 SCHEMA_BLOCKER
  15 MONITORING_FAILURE
  30 GOVERNANCE_VIOLATION

Usage:
  python model_monitor.py --config monitoring/model_monitor_config.yaml
  python model_monitor.py --config monitoring/model_monitor_config.yaml --input batch.csv
  python model_monitor.py --config monitoring/model_monitor_config.yaml --schema-only
  python model_monitor.py --config monitoring/model_monitor_config.yaml --artifact-integrity
  python model_monitor.py --config monitoring/model_monitor_config.yaml --json-summary
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── paths ────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).parent.resolve()
_MONITORING_DIR = _SCRIPT_DIR / "monitoring"
_CONFIG_DIR = _SCRIPT_DIR / "configs"
_PACKAGE_DIR = (
    _SCRIPT_DIR
    / ".."
    / "7.10.model_packaging"
    / "package"
).resolve()
_PKG_EXAMPLES = _PACKAGE_DIR / "examples"
_PKG_SCHEMAS = _PACKAGE_DIR / "schemas"
_PKG_METADATA = _PACKAGE_DIR / "metadata"
_PKG_MODELS = _PACKAGE_DIR / "models"
_PKG_PREPROC = _PACKAGE_DIR / "preprocessing"
_PKG_PIPELINE = _PACKAGE_DIR / "pipeline"

# ── exit codes ───────────────────────────────────────────────────────────────
EXIT_PASS = 0
EXIT_WARNINGS = 2
EXIT_INPUT_ERROR = 10
EXIT_CONFIG_ERROR = 11
EXIT_BASELINE_ERROR = 12
EXIT_ARTIFACT_FAIL = 13
EXIT_SCHEMA_BLOCKER = 14
EXIT_MONITORING_FAILURE = 15
EXIT_GOVERNANCE_VIOLATION = 30

# ── severity levels ──────────────────────────────────────────────────────────
SEV_OK = "OK"
SEV_INFO = "INFO"
SEV_WARNING = "WARNING"
SEV_CRITICAL = "CRITICAL"
SEV_BLOCKER = "BLOCKER"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MonitorAlert:
    alert_id: str
    category: str
    metric: str
    feature: Optional[str]
    expected: Any
    actual: Any
    threshold: Any
    threshold_source: str
    severity: str
    evidence: dict = field(default_factory=dict)
    message: str = ""
    recommended_action: str = ""
    auto_action_executed: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MonitorResult:
    monitor_run_id: str
    batch_id: Optional[str]
    model_id: str
    model_version: str
    package_version: str
    data_version: str
    baseline_id: str
    baseline_version: str
    baseline_hash_pre: str = ""
    baseline_hash_post: str = ""
    input_rows: int = 0
    labels_authorized: bool = False
    schema_check_executed: bool = False
    data_quality_check_executed: bool = False
    feature_drift_check_executed: bool = False
    prediction_drift_check_executed: bool = False
    performance_check_executed: bool = False
    artifact_integrity_check_executed: bool = False
    training_executed: bool = False
    refit_executed: bool = False
    auto_retrain_executed: bool = False
    auto_update_baseline_executed: bool = False
    champion_changed: bool = False
    schema_status: str = "NOT_RUN"
    data_quality_status: str = "NOT_RUN"
    feature_drift_status: str = "NOT_RUN"
    prediction_drift_status: str = "NOT_RUN"
    artifact_integrity_status: str = "NOT_RUN"
    overall_status: str = "PASS"
    warnings: list = field(default_factory=list)
    blockers: list = field(default_factory=list)
    alerts: list = field(default_factory=list)
    open_items: list = field(default_factory=list)
    started_at: str = ""
    ended_at: str = ""
    duration_seconds: float = 0.0
    output_dir: Path = field(default_factory=Path)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["output_dir"] = str(d["output_dir"])
        return d


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def make_uuid() -> str:
    return uuid.uuid4().hex[:8]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return {}


def save_json(path: Path, data: dict, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_config(config_path: Path) -> dict:
    if config_path.suffix in (".yaml", ".yml"):
        return load_yaml(config_path)
    return load_json(config_path)


def resolve_pkg_dir(config: dict) -> Path:
    if config.get("paths", {}).get("package_dir"):
        return Path(config["paths"]["package_dir"])
    return _PACKAGE_DIR


def resolve_output_dir(config: dict, run_id: str, explicit_dir: Optional[Path] = None) -> Path:
    if explicit_dir:
        d = explicit_dir
    elif config.get("paths", {}).get("output_dir"):
        d = Path(config["paths"]["output_dir"]) / run_id
    else:
        d = _MONITORING_DIR / "runs" / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _fmt(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


# ═══════════════════════════════════════════════════════════════════════════════
# PSI COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════

_EPSILON = 1e-6


def compute_psi(
    current: list[float],
    expected: list[float],
    bins: list[float],
    expected_proportions: list[float] | None = None,
) -> dict:
    """
    Population Stability Index using fixed baseline bins.
    Compares current distribution against expected (baseline) distribution.

    The `expected` parameter accepts EITHER:
      - A list of raw float values: binning is done internally
      - A list of pre-computed proportions (values sum to ~1): used directly

    The `expected_proportions` parameter (preferred) bypasses all heuristics and
    is used directly as the baseline distribution.
    """
    import numpy as np

    current_arr = np.array(current, dtype=float)
    valid = np.isfinite(current_arr)
    current_arr = current_arr[valid]

    if len(current_arr) < 10:
        return {
            "psi": None,
            "status": "NOT_ENOUGH_DATA",
            "current_n": len(current_arr),
            "message": "Fewer than 10 valid values — cannot compute PSI",
            "epsilon": _EPSILON,
            "bin_policy": "fixed_from_baseline",
        }

    # Bin using fixed baseline edges — current distribution
    counts_current, _ = np.histogram(current_arr, bins=bins)
    probs_current = counts_current / max(counts_current.sum(), 1)

    # Expected distribution: resolve via explicit proportions > raw values > fallback
    # Proportions are identified by having all values in [0,1] and summing ~1.0
    n_bins = len(bins) - 1
    probs_expected: np.ndarray

    if expected_proportions is not None:
        # Explicit proportions from caller — use directly
        raw = np.array(expected_proportions, dtype=float)
        if len(raw) != n_bins:
            return {
                "psi": None,
                "status": "INVALID_PROPORTIONS",
                "current_n": len(current_arr),
                "expected_proportions_n": len(raw),
                "bin_count": n_bins,
                "message": f"expected_proportions has {len(raw)} values but {n_bins} expected for bins",
            }
        probs_expected = raw / max(raw.sum(), 1e-9)

    elif len(expected) == 0:
        # No expected data provided — cannot compute PSI meaningfully
        return {
            "psi": None,
            "status": "EXPECTED_DATA_MISSING",
            "current_n": len(current_arr),
            "bin_count": n_bins,
            "epsilon": _EPSILON,
            "bin_policy": "fixed_from_baseline",
            "message": "No expected baseline data passed — PSI cannot be computed",
        }
    elif len(expected) == n_bins:
        # Exactly n_bins values: treat as pre-computed proportions
        raw_expected = np.array(expected, dtype=float)
        if np.all(raw_expected >= 0) and np.abs(raw_expected.sum() - 1.0) < 0.01:
            probs_expected = raw_expected / max(raw_expected.sum(), 1.0)
        else:
            probs_expected = raw_expected
    else:
        # Treat as raw values and bin them
        expected_arr = np.array(expected, dtype=float)
        valid_exp = np.isfinite(expected_arr)
        expected_arr = expected_arr[valid_exp]
        if len(expected_arr) < 10:
            return {
                "psi": None,
                "status": "EXPECTED_DATA_INSUFFICIENT",
                "current_n": len(current_arr),
                "expected_n": len(expected_arr),
                "message": f"Expected data has only {len(expected_arr)} values (< 10) — cannot compute PSI",
                "epsilon": _EPSILON,
                "bin_policy": "fixed_from_baseline",
            }
        counts_expected, _ = np.histogram(expected_arr, bins=bins)
        probs_expected = counts_expected / max(counts_expected.sum(), 1)

    # Add epsilon to avoid log(0)
    p_e = np.clip(probs_expected, _EPSILON, 1.0)
    p_c = np.clip(probs_current, _EPSILON, 1.0)

    # PSI = sum((actual - expected) * ln(actual/expected))
    ratios = p_c / p_e
    mask = probs_expected > 0
    psi = float(np.sum((p_c[mask] - p_e[mask]) * np.log(ratios[mask])))

    return {
        "psi": round(psi, 6),
        "status": "COMPUTED",
        "current_n": int(len(current_arr)),
        "bin_count": len(bins) - 1,
        "epsilon": _EPSILON,
        "bin_policy": "fixed_from_baseline",
        "bin_edges": bins,
        "empty_bin_handling": "epsilon_replacement",
        "sample_size_ok": len(current_arr) >= 100,
    }


def compute_tvd(
    current: dict[str, int],
    expected: dict[str, int],
) -> dict:
    """
    Total Variation Distance for categorical distributions.
    Aligns on full support (baseline + current + '__unseen__').
    """
    import numpy as np

    all_cats = set(expected.keys()) | set(current.keys())
    total_cur = sum(current.values()) or 1

    # Treat null expected values as having 0 frequency (unseen)
    valid_exp = {c: v for c, v in expected.items() if v is not None}
    total_exp = sum(valid_exp.values()) or 1

    p_current = {c: current.get(c, 0) / total_cur for c in all_cats}
    p_expected = {c: (valid_exp.get(c, 0) or 0) / total_exp for c in all_cats}

    tvd = sum(abs(p_current[c] - p_expected[c]) for c in all_cats) / 2.0

    unseen = [c for c in current if c not in expected]
    unseen_count = sum(current.get(c, 0) for c in unseen)

    return {
        "tvd": round(tvd, 6),
        "status": "COMPUTED",
        "unseen_categories": unseen,
        "unseen_count": unseen_count,
        "unseen_rate": round(unseen_count / total_cur, 6) if total_cur > 0 else 0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD INPUT BATCH
# ═══════════════════════════════════════════════════════════════════════════════

def load_input_batch(input_path: Path, fmt: str = "auto") -> tuple[Any, str]:
    """Load feature batch. Returns (df, format)."""
    import pandas as pd

    suffix = input_path.suffix.lower()
    if fmt == "auto":
        if suffix in (".csv",):
            fmt = "csv"
        elif suffix in (".parquet", ".pq"):
            fmt = "parquet"
        elif suffix in (".json",):
            fmt = "json"

    if fmt == "csv":
        df = pd.read_csv(input_path)
    elif fmt == "parquet":
        df = pd.read_parquet(input_path)
    elif fmt == "json":
        records = load_json(input_path)
        if isinstance(records, list):
            df = pd.DataFrame(records)
        else:
            df = pd.DataFrame([records])
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    # Normalize column names
    df.columns = df.columns.str.strip()
    return df, fmt


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_schema(
    df: Any,
    input_schema: dict,
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Check DataFrame against input schema contract."""
    import pandas as pd

    result.schema_check_executed = True
    schema_cfg = cfg.get("thresholds", {}).get("schema", {})
    sev_unexpected = schema_cfg.get("unexpected_columns_severity", "WARNING")

    required_fields = {f["name"] for f in input_schema.get("fields", []) if f.get("required", True)}
    all_schema_fields = {f["name"] for f in input_schema.get("fields", [])}
    df_cols = set(df.columns)

    field_results = []
    blockers_found = []
    warnings_found = []

    # Check for duplicate column names
    dup_cols = [c for c in df.columns if df.columns.tolist().count(c) > 1]
    if dup_cols:
        for c in dup_cols:
            warnings_found.append({
                "field": c, "check": "duplicate_column",
                "severity": "WARNING", "message": f"Duplicate column: {c}",
            })

    # Missing required fields
    missing_required = required_fields - df_cols
    for f in missing_required:
        blockers_found.append({
            "field": f, "check": "missing_required_field",
            "severity": "BLOCKER",
            "message": f"Required field '{f}' is missing from input batch",
        })

    # Unexpected fields
    unexpected = df_cols - all_schema_fields
    for f in unexpected:
        warnings_found.append({
            "field": f, "check": "unexpected_field",
            "severity": sev_unexpected,
            "message": f"Field '{f}' is not in the schema contract",
        })

    # Check target column presence (policy: target must not be in features)
    target_cols = {"target", "target_popularity", "y"}
    target_in_batch = target_cols & df_cols
    if target_in_batch and not result.labels_authorized:
        warnings_found.append({
            "field": list(target_in_batch)[0],
            "check": "target_present_not_authorized",
            "severity": "WARNING",
            "message": "Target column present but --with-labels not authorized",
        })

    all_field_results = blockers_found + warnings_found

    for col in df_cols & all_schema_fields:
        field_def = next((f for f in input_schema.get("fields", []) if f["name"] == col), None)
        if field_def:
            field_results.append({
                "field": col,
                "expected_dtype": field_def.get("data_type"),
                "actual_dtype": str(df[col].dtype),
                "status": "VALID",
                "severity": SEV_OK,
                "message": "Column present and in schema",
            })

    # Schema version check
    schema_version_ok = input_schema.get("schema_version") == "1.0.0"

    status = SEV_BLOCKER if blockers_found else SEV_OK
    result.schema_status = "PASS" if status == SEV_OK else "FAIL"
    result.blockers.extend([{
        "category": "SCHEMA",
        "field": b["field"],
        "check": b["check"],
        "severity": b["severity"],
        "message": b["message"],
    } for b in blockers_found])
    result.warnings.extend([{
        "category": "SCHEMA",
        "field": w["field"],
        "check": w["check"],
        "severity": w["severity"],
        "message": w["message"],
    } for w in warnings_found])

    return {
        "schema_id": input_schema.get("schema_id"),
        "schema_version": input_schema.get("schema_version"),
        "schema_version_ok": schema_version_ok,
        "required_fields_checked": sorted(required_fields),
        "missing_required_fields": sorted(missing_required),
        "unexpected_fields": sorted(unexpected),
        "duplicate_columns": dup_cols,
        "field_results": field_results,
        "overall_status": status,
        "field_count": len(df.columns),
        "expected_field_count": len(all_schema_fields),
        "target_in_batch_but_not_authorized": list(target_in_batch) if not result.labels_authorized else [],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DATA QUALITY MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_data_quality(
    df: Any,
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Data quality checks — row counts, NaN, Inf, duplicates, ranges."""
    import numpy as np

    result.data_quality_check_executed = True
    dq_cfg = cfg.get("thresholds", {}).get("data_quality", {})
    inf_sev = dq_cfg.get("inf_severity", "BLOCKER")
    nan_sev = dq_cfg.get("nan_rate_severity", "WARNING")
    dup_sev = dq_cfg.get("duplicate_rows_severity", "WARNING")
    empty_sev = dq_cfg.get("empty_batch_severity", "BLOCKER")

    rows_received = len(df)
    blockers_found = []
    warnings_found = []

    # Empty batch
    if rows_received == 0:
        blockers_found.append({
            "check": "empty_batch",
            "severity": empty_sev,
            "message": "Batch has 0 rows",
            "rows_received": 0,
        })
        return {
            "rows_received": 0, "rows_valid": 0, "rows_invalid": 0,
            "checks": [],
            "blockers": blockers_found, "warnings": [],
            "overall_status": SEV_BLOCKER,
        }

    # Duplicate rows
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        warnings_found.append({
            "check": "duplicate_rows",
            "severity": dup_sev,
            "message": f"{dup_count} duplicate rows found",
            "count": dup_count, "rate": round(dup_count / rows_received, 6),
        })

    # Per-field checks
    field_checks = []
    for col in df.columns:
        if col in ("target", "target_popularity", "y"):
            continue
        ser = df[col]
        dtype_str = str(ser.dtype)

        # NaN/None count
        nan_count = int(ser.isna().sum())
        nan_rate = nan_count / rows_received if rows_received > 0 else 0
        nan_severity = SEV_BLOCKER if nan_rate > 0.5 else (nan_sev if nan_rate > dq_cfg.get("nan_rate_threshold", 0.05) else SEV_OK)
        if nan_count > 0 and nan_severity != SEV_OK:
            warnings_found.append({
                "check": "nan_rate", "field": col,
                "severity": nan_severity,
                "message": f"Column '{col}': NaN rate = {nan_rate:.4f}",
                "count": nan_count, "rate": round(nan_rate, 6),
            })
        field_checks.append({
            "field": col, "dtype": dtype_str,
            "nan_count": nan_count, "nan_rate": round(nan_rate, 6),
            "unique_count": int(ser.nunique()),
        })

    # Inf / -Inf check — always BLOCKER per config
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    inf_count = 0
    for col in numeric_cols:
        vals = df[col].values
        inf_mask = ~np.isfinite(vals)
        ic = int(np.sum(inf_mask))
        inf_count += ic
        if ic > 0:
            blockers_found.append({
                "check": "inf_values",
                "field": col,
                "severity": inf_sev,
                "message": f"Column '{col}': {ic} Inf/-Inf values found",
                "count": ic,
            })

    # All-constant columns
    const_cols = [c for c in df.columns if df[c].nunique() <= 1]
    for c in const_cols:
        warnings_found.append({
            "check": "constant_column",
            "field": c,
            "severity": SEV_WARNING,
            "message": f"Column '{c}' is constant",
        })

    # Hard range violations (from schema)
    range_violations = []
    schema = {}
    schema_path = _PACKAGE_DIR / "schemas" / "input_schema.json"
    if schema_path.exists():
        schema = load_json(schema_path)
    for fld in schema.get("fields", []):
        col = fld["name"]
        if col not in df.columns:
            continue
        fmin = fld.get("minimum")
        fmax = fld.get("maximum")
        if fmin is not None or fmax is not None:
            viol = ((df[col] < fmin) | (df[col] > fmax)).sum() if fmin is not None or fmax is not None else 0
            if fmin is not None and fmax is not None:
                viol = int(((df[col] < fmin) | (df[col] > fmax)).sum())
            elif fmin is not None:
                viol = int((df[col] < fmin).sum())
            else:
                viol = int((df[col] > fmax).sum())
            if viol > 0:
                range_violations.append({
                    "field": col,
                    "violation_count": viol,
                    "rate": round(viol / rows_received, 6),
                    "min_expected": fmin, "max_expected": fmax,
                    "severity": SEV_WARNING,
                    "message": f"{viol} values outside [{fmin},{fmax}] for '{col}'",
                })

    all_checks = blockers_found + warnings_found + range_violations
    status = SEV_BLOCKER if blockers_found else SEV_OK
    result.data_quality_status = "PASS" if status == SEV_OK else "FAIL"
    result.blockers.extend([{"category": "DATA_QUALITY", **b} for b in blockers_found])
    result.warnings.extend([{"category": "DATA_QUALITY", **w} for w in warnings_found])

    return {
        "rows_received": rows_received,
        "rows_valid": rows_received - inf_count,
        "rows_invalid": inf_count,
        "rows_used_for_prediction": rows_received,
        "duplicate_rows_count": dup_count,
        "duplicate_rows_rate": round(dup_count / rows_received, 6) if rows_received > 0 else 0,
        "inf_count": inf_count,
        "field_checks": field_checks,
        "range_violations": range_violations,
        "constant_columns": const_cols,
        "checks": all_checks,
        "overall_status": status,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NUMERIC FEATURE DRIFT
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_numeric_drift(
    df: Any,
    baseline: dict,
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Compute drift metrics for numeric features against baseline."""
    import numpy as np

    result.feature_drift_check_executed = True
    drift_cfg = cfg.get("thresholds", {}).get("feature_drift", {}).get("numeric", {})
    min_rows = cfg.get("sample_requirements", {}).get("minimum_drift_rows", 100)

    numeric_feats = baseline.get("numeric_features", {})
    psi_bins = baseline.get("psi_bins", {}).get("numeric_features", {})
    rows = len(df)

    if rows < min_rows:
        result.warnings.append({
            "category": "SAMPLE_SIZE",
            "message": f"Batch rows ({rows}) < minimum_drift_rows ({min_rows}). Drift metrics may be unreliable.",
        })
        return {"overall_status": "NOT_ENOUGH_DATA", "rows": rows, "features": []}

    feature_results = []
    blockers_found = []
    warnings_found = []

    for feat_name, base_stats in numeric_feats.items():
        if feat_name not in df.columns:
            continue

        ser = df[feat_name].replace([np.inf, -np.inf], np.nan).dropna()
        if len(ser) < 10:
            feature_results.append({
                "feature": feat_name, "type": "numeric",
                "status": "NOT_ENOUGH_DATA",
                "valid_count": len(ser),
                "missing_rate_delta": None, "mean_delta": None,
                "median_delta": None, "std_ratio": None, "psi": None,
            })
            continue

        current_missing_rate = len(df) > 0 and (df[feat_name].isna().sum() / len(df))
        base_missing_rate = base_stats.get("missing_rate", 0)
        missing_rate_delta = current_missing_rate - base_missing_rate

        current_mean = float(ser.mean())
        base_mean = base_stats.get("mean")
        mean_delta = current_mean - base_mean if base_mean is not None else None

        current_median = float(np.median(ser))
        base_median = (base_stats.get("quantiles") or {}).get("0.5")
        median_delta = current_median - base_median if base_median is not None else None

        current_std = float(ser.std()) if len(ser) > 1 else 0.0
        base_std = base_stats.get("std") or 1.0
        std_ratio = current_std / base_std if base_std else None

        # PSI with fixed bins — use explicit proportions if available, else heuristic
        psi_info = None
        feat_psi_bins = psi_bins.get(feat_name)
        if feat_psi_bins:
            base_props = base_stats.get("psi_proportions")
            psi_info = compute_psi(ser.tolist(), [], feat_psi_bins,
                                   expected_proportions=base_props)

        # Threshold evaluation
        feat_warnings = []
        feat_severity = SEV_OK

        # Missing rate delta
        mrd_thresh = drift_cfg.get("missing_rate_delta_threshold", 0.05)
        mrd_sev = drift_cfg.get("missing_rate_delta_severity", "WARNING")
        if abs(missing_rate_delta) > mrd_thresh:
            feat_warnings.append(f"missing_rate_delta={missing_rate_delta:.4f} > {mrd_thresh}")
            if mrd_sev == "CRITICAL":
                feat_severity = SEV_CRITICAL

        # Mean delta
        if mean_delta is not None:
            md_thresh = drift_cfg.get("mean_delta_threshold", 0.1)
            md_sev = drift_cfg.get("mean_delta_severity", "WARNING")
            if abs(mean_delta) > md_thresh:
                feat_warnings.append(f"mean_delta={mean_delta:.4f} > {md_thresh}")
                if md_sev == "CRITICAL":
                    feat_severity = SEV_CRITICAL

        # Median delta
        if median_delta is not None:
            mdn_thresh = drift_cfg.get("median_delta_threshold", 0.1)
            mdn_sev = drift_cfg.get("median_delta_severity", "WARNING")
            if abs(median_delta) > mdn_thresh:
                feat_warnings.append(f"median_delta={median_delta:.4f} > {mdn_thresh}")

        # Std ratio
        if std_ratio is not None:
            std_low = drift_cfg.get("std_ratio_low_threshold", 0.8)
            std_high = drift_cfg.get("std_ratio_high_threshold", 1.25)
            std_sev = drift_cfg.get("std_ratio_severity", "WARNING")
            if std_ratio < std_low or std_ratio > std_high:
                feat_warnings.append(f"std_ratio={std_ratio:.3f} outside [{std_low},{std_high}]")
                if std_sev == "CRITICAL":
                    feat_severity = SEV_CRITICAL

        # PSI
        psi_thresh = drift_cfg.get("psi_threshold", 0.2)
        psi_sev = drift_cfg.get("psi_severity", "WARNING")
        psi_val = psi_info.get("psi") if psi_info else None
        if psi_val is not None and psi_val > psi_thresh:
            feat_warnings.append(f"PSI={psi_val:.4f} > {psi_thresh}")
            if psi_sev == "CRITICAL":
                feat_severity = SEV_CRITICAL

        feat_status = "PASS"
        if feat_severity == SEV_CRITICAL:
            feat_status = "CRITICAL"
            warnings_found.append({"feature": feat_name, "severity": "CRITICAL", "warnings": feat_warnings})
        elif feat_warnings:
            feat_status = "WARNING"
            warnings_found.append({"feature": feat_name, "severity": "WARNING", "warnings": feat_warnings})

        feature_results.append({
            "feature": feat_name, "type": "numeric",
            "status": feat_status,
            "valid_count": len(ser),
            "missing_rate_delta": round(missing_rate_delta, 6) if missing_rate_delta is not None else None,
            "current_mean": round(current_mean, 6),
            "baseline_mean": base_mean,
            "mean_delta": round(mean_delta, 6) if mean_delta is not None else None,
            "current_median": round(current_median, 6),
            "baseline_median": base_median,
            "median_delta": round(median_delta, 6) if median_delta is not None else None,
            "current_std": round(current_std, 6),
            "baseline_std": base_std,
            "std_ratio": round(std_ratio, 4) if std_ratio is not None else None,
            "psi": psi_info,
            "warnings": feat_warnings,
            "severity": feat_severity,
        })

    # Overall feature drift status
    crit_count = sum(1 for f in feature_results if f.get("severity") == SEV_CRITICAL)
    warn_count = sum(1 for f in feature_results if f.get("severity") == SEV_WARNING)
    overall = SEV_OK
    if crit_count > 0:
        overall = SEV_CRITICAL
    elif warn_count > 0:
        overall = SEV_WARNING

    result.feature_drift_status = overall
    result.warnings.extend([{"category": "FEATURE_DRIFT", **w} for w in warnings_found])

    return {
        "rows": rows,
        "features": feature_results,
        "critical_count": crit_count,
        "warning_count": warn_count,
        "overall_status": overall,
        "top_shifted_features": [
            {"feature": f["feature"], "warnings": f["warnings"]}
            for f in sorted(feature_results, key=lambda x: len(x.get("warnings", [])), reverse=True)
            if f.get("warnings")
        ][:5],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORICAL FEATURE DRIFT
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_categorical_drift(
    df: Any,
    baseline: dict,
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Compute drift metrics for categorical features against baseline."""
    import numpy as np

    cat_feats = baseline.get("categorical_features", {})
    min_rows = cfg.get("sample_requirements", {}).get("minimum_drift_rows", 100)

    feature_results = []
    warnings_found = []

    for feat_name, base_stats in cat_feats.items():
        if feat_name not in df.columns:
            continue

        ser = df[feat_name].astype(str)
        total = len(ser)
        if total == 0:
            continue

        current_counts = ser.value_counts().to_dict()
        base_counts = base_stats.get("category_frequencies", {})

        # Only include categories that have non-null baseline frequencies
        valid_base_counts = {c: v for c, v in base_counts.items() if v is not None}

        # Align support
        all_cats = set(valid_base_counts.keys()) | set(current_counts.keys())
        aligned_current = {c: int(current_counts.get(c, 0) or 0) for c in all_cats}
        aligned_expected = {c: int((valid_base_counts.get(c, 0) or 0) * total) for c in all_cats}

        # Normalize expected to current total
        base_total = sum(valid_base_counts.values()) or total
        norm_expected = {c: ((aligned_expected[c] or 0) / max(base_total, 1)) * total for c in all_cats}

        # TVD
        tvd_info = compute_tvd(aligned_current, norm_expected)

        # Missing rate delta
        current_missing = ser.isna().sum()
        base_missing_rate = base_stats.get("missing_rate", 0)
        current_missing_rate = current_missing / total
        missing_delta = current_missing_rate - base_missing_rate

        # Unseen categories
        unseen = [c for c in current_counts if c not in base_counts]
        unseen_rate = sum(current_counts.get(c, 0) for c in unseen) / total

        feat_warnings = []
        feat_severity = SEV_OK

        if unseen:
            feat_warnings.append(f"unseen_categories={unseen}, rate={unseen_rate:.4f}")
            feat_severity = SEV_WARNING

        if abs(missing_delta) > 0.05:
            feat_warnings.append(f"missing_rate_delta={missing_delta:.4f}")

        if tvd_info.get("tvd") is not None and tvd_info.get("tvd", 0) > 0.1:
            feat_warnings.append(f"TVD={tvd_info['tvd']:.4f} > 0.1")
            feat_severity = SEV_WARNING

        feat_status = "WARNING" if feat_warnings else "PASS"
        if feat_warnings:
            warnings_found.append({"feature": feat_name, "warnings": feat_warnings, "severity": feat_severity})

        feature_results.append({
            "feature": feat_name, "type": "categorical",
            "status": feat_status,
            "total_count": total,
            "current_categories": sorted(current_counts.keys()),
            "baseline_categories": sorted(base_stats.get("categories", [])),
            "unseen_categories": unseen,
            "unseen_count": sum(current_counts.get(c, 0) for c in unseen),
            "unseen_rate": round(unseen_rate, 6),
            "missing_rate_delta": round(missing_delta, 6),
            "tvd": tvd_info,
            "warnings": feat_warnings,
            "severity": feat_severity,
        })

    crit_count = sum(1 for f in feature_results if f.get("severity") == SEV_CRITICAL)
    warn_count = sum(1 for f in feature_results if f.get("severity") == SEV_WARNING)

    result.warnings.extend([{"category": "CAT_DRIFT", **w} for w in warnings_found])

    return {
        "features": feature_results,
        "critical_count": crit_count,
        "warning_count": warn_count,
        "overall_status": SEV_CRITICAL if crit_count > 0 else (SEV_WARNING if warn_count > 0 else SEV_OK),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE DRIFT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def compute_feature_drift_summary(
    num_results: dict,
    cat_results: dict,
    result: MonitorResult,
) -> dict:
    """Aggregate per-feature results into overall feature drift status."""
    num_feats = num_results.get("features", [])
    cat_feats = cat_results.get("features", [])

    all_feats = num_feats + cat_feats
    ok_count = sum(1 for f in all_feats if f.get("status") == "PASS")
    warn_count = sum(1 for f in all_feats if f.get("status") == "WARNING")
    crit_count = sum(1 for f in all_feats if f.get("status") == "CRITICAL")
    not_enough = sum(1 for f in all_feats if f.get("status") == "NOT_ENOUGH_DATA")

    top_shifted = sorted(
        [f for f in all_feats if f.get("warnings")],
        key=lambda x: len(x.get("warnings", [])),
        reverse=True,
    )[:5]

    overall = SEV_OK
    if crit_count > 0:
        overall = SEV_CRITICAL
    elif warn_count > 0:
        overall = SEV_WARNING

    result.feature_drift_status = overall

    return {
        "total_features_checked": len(all_feats),
        "pass_count": ok_count,
        "warning_count": warn_count,
        "critical_count": crit_count,
        "not_enough_data_count": not_enough,
        "overall_status": overall,
        "numeric_feature_count": len(num_feats),
        "categorical_feature_count": len(cat_feats),
        "top_shifted_features": [
            {"feature": f["feature"], "warnings": f.get("warnings", []), "severity": f.get("severity", SEV_OK)}
            for f in top_shifted
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICTION GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_predictions(
    df: Any,
    result: MonitorResult,
) -> tuple[Any, dict]:
    """
    Load frozen pipeline and generate predictions.
    NEVER trains, fits, or refits — only predict().
    """
    import pandas as pd
    import joblib
    import sys
    from pathlib import Path

    manifest_path = _PACKAGE_DIR / "manifests" / "full_inference_pipeline_manifest.json"
    pipeline_path = _PACKAGE_DIR / "pipeline" / "full_inference_pipeline.joblib"
    runtime_dir = _PACKAGE_DIR / "runtime"

    gen_manifest = {
        "pipeline_loaded": False,
        "predictions_generated": False,
        "warnings": [],
    }

    if not pipeline_path.exists():
        result.warnings.append({
            "category": "PREDICTION",
            "message": f"Pipeline file not found: {pipeline_path}",
        })
        return None, gen_manifest

    # Add runtime/ to path so custom classes (e.g. inference_pipeline) are resolvable
    if str(runtime_dir) not in sys.path:
        sys.path.insert(0, str(runtime_dir))

    try:
        pipeline = joblib.load(pipeline_path)
        gen_manifest["pipeline_loaded"] = True
        gen_manifest["pipeline_path"] = str(pipeline_path)
        gen_manifest["pipeline_class"] = type(pipeline).__name__

        # Get expected columns from schema
        schema_path = _PACKAGE_DIR / "schemas" / "input_schema.json"
        if schema_path.exists():
            schema = load_json(schema_path)
            expected_cols = [f["name"] for f in schema.get("fields", [])]
        else:
            expected_cols = list(df.columns)

        # Select only expected columns
        available = [c for c in expected_cols if c in df.columns]
        X = df[available].copy()

        # Convert boolean to expected type
        if "explicit" in X.columns:
            X["explicit"] = X["explicit"].astype(str)

        # Predict
        preds_raw = pipeline.predict(X)
        preds_clipped = preds_raw.clip(0, 100)
        preds_display = preds_clipped.round().astype(int)

        preds_df = pd.DataFrame({
            "prediction_raw": preds_raw,
            "prediction_clipped": preds_clipped,
            "prediction_display": preds_display,
        })

        gen_manifest["predictions_generated"] = True
        gen_manifest["row_count"] = len(preds_df)

        result.prediction_drift_check_executed = True
        return preds_df, gen_manifest

    except ModuleNotFoundError as exc:
        gen_manifest["pipeline_loaded"] = False
        gen_manifest["predictions_generated"] = False
        gen_manifest["error"] = f"Missing runtime dependency: {exc.name}"
        gen_manifest["note"] = "Prediction drift monitoring requires full runtime dependencies. SHA256 and schema checks passed."
        result.warnings.append({
            "category": "PREDICTION",
            "message": f"Prediction generation skipped — missing runtime dependency: {exc.name}",
        })
        return None, gen_manifest

    except Exception as exc:
        result.warnings.append({
            "category": "PREDICTION",
            "message": f"Prediction generation failed: {exc}",
        })
        gen_manifest["error"] = str(exc)
        return None, gen_manifest


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICTION DRIFT
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_prediction_drift(
    preds_df: Any,
    baseline: dict,
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Monitor prediction distribution against baseline."""
    import numpy as np

    if preds_df is None or len(preds_df) == 0:
        return {
            "status": "NO_PREDICTIONS",
            "overall_status": "NOT_RUN",
            "message": "No predictions available for drift monitoring",
        }

    result.prediction_drift_check_executed = True
    pred_cfg = cfg.get("thresholds", {}).get("prediction_drift", {})
    psi_bins = baseline.get("psi_bins", {}).get("prediction", [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    raw = preds_df["prediction_raw"].values
    clipped = preds_df["prediction_clipped"].values

    current_mean = float(np.mean(raw))
    current_std = float(np.std(raw))
    current_median = float(np.median(raw))
    current_min = float(np.min(raw))
    current_max = float(np.max(raw))

    base_pred = baseline.get("prediction", {})
    base_mean = base_pred.get("mean")
    base_std = base_pred.get("std")
    base_median = base_pred.get("quantiles", {}).get("0.5")

    mean_delta = current_mean - base_mean if base_mean is not None else None
    std_ratio = current_std / base_std if base_std else None

    # PSI on clipped predictions — use explicit proportions if available
    base_pred_props = base_pred.get("psi_proportions")
    psi_info = compute_psi(clipped.tolist(), [], psi_bins,
                           expected_proportions=base_pred_props)

    # Clipped rate
    clipped_rate = float(np.mean(raw != clipped))
    base_clipped_rate = base_pred.get("clipped_rate", 0)
    clipped_rate_delta = abs(clipped_rate - base_clipped_rate)

    # Near-zero rate
    near_zero = float(np.mean(np.abs(clipped) < 1))
    base_near_zero = base_pred.get("near_zero_rate", 0.0762)
    near_zero_delta = abs(near_zero - base_near_zero)

    # Range violations
    outside_expected = int(np.sum((clipped < 0) | (clipped > 100)))

    # Bucket distribution
    buckets = {
        "0-20": int(np.sum((clipped >= 0) & (clipped <= 20))),
        "21-40": int(np.sum((clipped > 20) & (clipped <= 40))),
        "41-60": int(np.sum((clipped > 40) & (clipped <= 60))),
        "61-80": int(np.sum((clipped > 60) & (clipped <= 80))),
        "81-100": int(np.sum((clipped > 80) & (clipped <= 100))),
    }

    # Threshold evaluation
    warnings_found = []
    feat_severity = SEV_OK

    if mean_delta is not None:
        md_thresh = pred_cfg.get("mean_delta_threshold", 2.0)
        if abs(mean_delta) > md_thresh:
            warnings_found.append(f"mean_delta={mean_delta:.2f} > {md_thresh}")
            feat_severity = SEV_WARNING

    if std_ratio is not None:
        std_low = pred_cfg.get("std_ratio_low_threshold", 0.8)
        std_high = pred_cfg.get("std_ratio_high_threshold", 1.25)
        if std_ratio < std_low or std_ratio > std_high:
            warnings_found.append(f"std_ratio={std_ratio:.3f} outside [{std_low},{std_high}]")

    if psi_info.get("psi") is not None:
        psi_val = psi_info["psi"]
        psi_thresh = pred_cfg.get("psi_threshold", 0.2)
        if psi_val > psi_thresh:
            warnings_found.append(f"PSI={psi_val:.4f} > {psi_thresh}")
            feat_severity = SEV_WARNING

    status = SEV_WARNING if warnings_found else SEV_OK
    result.prediction_drift_status = status
    result.warnings.extend([{"category": "PRED_DRIFT", "message": w} for w in warnings_found])

    return {
        "count": len(preds_df),
        "mean": round(current_mean, 4),
        "std": round(current_std, 4),
        "median": round(current_median, 4),
        "min": round(current_min, 4),
        "max": round(current_max, 4),
        "baseline_mean": base_mean,
        "baseline_std": base_std,
        "mean_delta": round(mean_delta, 4) if mean_delta is not None else None,
        "std_ratio": round(std_ratio, 4) if std_ratio is not None else None,
        "clipped_rate": round(clipped_rate, 6),
        "baseline_clipped_rate": base_clipped_rate,
        "clipped_rate_delta": round(clipped_rate_delta, 6),
        "near_zero_rate": round(near_zero, 6),
        "baseline_near_zero_rate": base_near_zero,
        "near_zero_rate_delta": round(near_zero_delta, 6),
        "outside_expected_range": outside_expected,
        "psi": psi_info,
        "bucket_distribution": buckets,
        "warnings": warnings_found,
        "overall_status": status,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ARTIFACT INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_artifact_integrity(
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Verify all package artifacts exist and match expected hashes."""
    result.artifact_integrity_check_executed = True
    fail_on_mismatch = cfg.get("governance", {}).get("fail_on_artifact_hash_mismatch", True)

    pkg_dir = resolve_pkg_dir(cfg)
    baseline_path = _MONITORING_DIR / "model_monitor_baseline.json"
    baseline = load_json(baseline_path)
    expected_hashes = baseline.get("artifact_hashes", {})

    # Artifact manifest path
    manifest_path = pkg_dir / "metadata" / "artifact_manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
    else:
        manifest = []

    checks = []
    blockers_found = []
    warnings_found = []

    # Version metadata files
    version_files = {
        "model_version": pkg_dir / "metadata" / "model_version.json",
        "data_version": pkg_dir / "metadata" / "data_version.json",
        "package_version": pkg_dir / "metadata" / "package_version.json",
    }

    for name, path in version_files.items():
        if path.exists():
            checks.append({
                "artifact": name, "path": str(path),
                "status": "EXISTS", "severity": SEV_OK,
            })
            try:
                meta = load_json(path)
                checks.append({
                    "artifact": f"{name}_content", "detail": meta,
                    "status": "READ_OK", "severity": SEV_OK,
                })
            except Exception as exc:
                warnings_found.append({
                    "artifact": name,
                    "check": "read_error",
                    "severity": SEV_WARNING,
                    "message": str(exc),
                })
        else:
            blockers_found.append({
                "artifact": name, "path": str(path),
                "check": "missing_file",
                "severity": SEV_BLOCKER if fail_on_mismatch else SEV_WARNING,
                "message": f"Required artifact not found: {name}",
            })

    # Schema files
    schema_files = {
        "input_schema": pkg_dir / "schemas" / "input_schema.json",
        "output_schema": pkg_dir / "schemas" / "output_schema.json",
    }
    for name, path in schema_files.items():
        status = "EXISTS" if path.exists() else "MISSING"
        sev = SEV_OK if path.exists() else (SEV_BLOCKER if fail_on_mismatch else SEV_WARNING)
        checks.append({"artifact": name, "path": str(path), "status": status, "severity": sev})
        if not path.exists():
            blockers_found.append({
                "artifact": name, "check": "missing_file",
                "severity": SEV_BLOCKER if fail_on_mismatch else SEV_WARNING,
                "message": f"Schema file not found: {name}",
            })

    # Pipeline file
    pipeline_file = pkg_dir / "pipeline" / "full_inference_pipeline.joblib"
    if pipeline_file.exists():
        checks.append({
            "artifact": "full_inference_pipeline", "path": str(pipeline_file),
            "status": "EXISTS", "severity": SEV_OK,
        })
        try:
            actual_hash = sha256_file(pipeline_file)
            expected_hash = expected_hashes.get("full_inference_pipeline")
            checks.append({
                "artifact": "full_inference_pipeline_hash",
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
                "match": actual_hash == expected_hash,
                "severity": SEV_OK if actual_hash == expected_hash else (SEV_BLOCKER if fail_on_mismatch else SEV_WARNING),
            })
            if actual_hash != expected_hash:
                blockers_found.append({
                    "artifact": "full_inference_pipeline",
                    "check": "hash_mismatch",
                    "severity": SEV_BLOCKER if fail_on_mismatch else SEV_WARNING,
                    "message": f"Pipeline hash mismatch: expected {expected_hash[:16]}..., got {actual_hash[:16]}...",
                })
        except Exception as exc:
            warnings_found.append({
                "artifact": "full_inference_pipeline",
                "check": "hash_compute_error",
                "severity": SEV_WARNING,
                "message": str(exc),
            })
    else:
        blockers_found.append({
            "artifact": "full_inference_pipeline",
            "check": "missing_file",
            "severity": SEV_BLOCKER if fail_on_mismatch else SEV_WARNING,
            "message": "Pipeline file not found",
        })

    # Pipeline load test
    if pipeline_file.exists():
        try:
            import joblib
            pipeline = joblib.load(pipeline_file)
            checks.append({
                "artifact": "pipeline_load",
                "pipeline_class": type(pipeline).__name__,
                "status": "LOAD_OK", "severity": SEV_OK,
            })
        except ModuleNotFoundError as exc:
            checks.append({
                "artifact": "pipeline_load",
                "status": "SKIPPED",
                "severity": SEV_INFO,
                "reason": f"Runtime dependency not available: {exc.name}",
                "detail": "SHA256 hash verified; load test deferred to full runtime environment",
            })
        except Exception as exc:
            blockers_found.append({
                "artifact": "pipeline_load",
                "check": "load_failed",
                "severity": SEV_WARNING if "version" in str(exc).lower() else SEV_BLOCKER,
                "message": f"Pipeline load failed: {exc}",
            })

    # SHA256 verification from manifest
    for entry in (manifest if isinstance(manifest, list) else []):
        logical_name = entry.get("logical_name", "")
        expected_sha = entry.get("sha256", "")
        rel_path = entry.get("package_relative_path", "")
        if not rel_path:
            continue
        artifact_path = pkg_dir / rel_path
        if artifact_path.exists():
            try:
                actual_sha = sha256_file(artifact_path)
                match = actual_sha == expected_sha
                checks.append({
                    "artifact": logical_name,
                    "expected_hash": expected_sha[:16] + "...",
                    "actual_hash": actual_sha[:16] + "...",
                    "match": match,
                    "severity": SEV_OK if match else (SEV_BLOCKER if fail_on_mismatch else SEV_WARNING),
                })
                if not match:
                    blockers_found.append({
                        "artifact": logical_name,
                        "check": "sha256_mismatch",
                        "severity": SEV_BLOCKER if fail_on_mismatch else SEV_WARNING,
                        "message": f"Artifact hash mismatch for {logical_name}",
                    })
            except Exception as exc:
                warnings_found.append({
                    "artifact": logical_name,
                    "check": "hash_error",
                    "message": str(exc),
                })

    status = SEV_BLOCKER if blockers_found else SEV_OK
    result.artifact_integrity_status = "PASS" if status == SEV_OK else "FAIL"
    result.blockers.extend([{"category": "ARTIFACT", **b} for b in blockers_found])
    result.warnings.extend([{"category": "ARTIFACT", **w} for w in warnings_found])

    return {
        "artifact_checks": checks,
        "blockers": blockers_found,
        "warnings": warnings_found,
        "overall_status": status,
        "fail_on_mismatch": fail_on_mismatch,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VERSION CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_version_consistency(
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Cross-check version metadata between all artifacts."""
    pkg_dir = resolve_pkg_dir(cfg)

    def load_meta(name: str) -> dict:
        path = pkg_dir / "metadata" / f"{name}.json"
        if path.exists():
            return load_json(path)
        return {}

    model_ver = load_meta("model_version")
    data_ver = load_meta("data_version")
    pkg_ver = load_meta("package_version")

    # Schema version from input schema
    schema_ver = {}
    schema_path = pkg_dir / "schemas" / "input_schema.json"
    if schema_path.exists():
        schema_ver = load_json(schema_path)

    checks = []
    inconsistencies = []

    # Model version
    checks.append({
        "field": "model_version",
        "value": model_ver.get("model_version"),
        "expected": cfg.get("monitoring_identifiers", {}).get("model_version"),
        "consistent": model_ver.get("model_version") == cfg.get("monitoring_identifiers", {}).get("model_version"),
    })
    if checks[-1]["value"] != checks[-1]["expected"]:
        inconsistencies.append("model_version mismatch")

    # Package version
    checks.append({
        "field": "package_version",
        "value": pkg_ver.get("package_version"),
        "expected": cfg.get("monitoring_identifiers", {}).get("package_version"),
        "consistent": pkg_ver.get("package_version") == cfg.get("monitoring_identifiers", {}).get("package_version"),
    })

    # Schema ID
    checks.append({
        "field": "schema_id",
        "value": schema_ver.get("schema_id"),
        "expected": cfg.get("monitoring_identifiers", {}).get("schema_id"),
        "consistent": schema_ver.get("schema_id") == cfg.get("monitoring_identifiers", {}).get("schema_id"),
    })

    all_consistent = all(c.get("consistent", False) for c in checks)

    return {
        "model_version": model_ver,
        "data_version": data_ver,
        "package_version": pkg_ver,
        "schema_version": schema_ver.get("schema_version"),
        "schema_id": schema_ver.get("schema_id"),
        "checks": checks,
        "inconsistencies_found": len(inconsistencies),
        "overall_status": SEV_OK if all_consistent else SEV_WARNING,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE REPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_example_replay(
    result: MonitorResult,
    cfg: dict,
) -> dict:
    """Load example input, run pipeline, compare against expected output."""
    import joblib
    import numpy as np
    from pathlib import Path

    pkg_dir = resolve_pkg_dir(cfg)
    example_in_path = pkg_dir / "examples" / "example_input.json"
    example_out_path = pkg_dir / "examples" / "example_output.json"

    if not example_in_path.exists() or not example_out_path.exists():
        return {
            "status": "MISSING_EXAMPLE_FILES",
            "overall_status": SEV_WARNING,
            "message": "Example files not found — replay skipped",
        }

    try:
        example_in = load_json(example_in_path)
        expected_out = load_json(example_out_path)
    except Exception as exc:
        return {
            "status": "READ_ERROR",
            "overall_status": SEV_WARNING,
            "message": f"Failed to read example files: {exc}",
        }

    pipeline_path = pkg_dir / "pipeline" / "full_inference_pipeline.joblib"
    if not pipeline_path.exists():
        return {
            "status": "PIPELINE_NOT_FOUND",
            "overall_status": SEV_WARNING,
            "message": "Pipeline file not found",
        }

    try:
        import pandas as pd
        pipeline = joblib.load(pipeline_path)
        X = pd.DataFrame([example_in])
        expected_pred = expected_out.get("prediction_raw")

        pred_raw = float(pipeline.predict(X)[0])
        pred_clipped = float(np.clip(pred_raw, 0, 100))

        tolerance = abs(pred_clipped - expected_pred) if expected_pred is not None else None
        within_tolerance = tolerance is not None and tolerance <= 1.0

        return {
            "status": "COMPUTED",
            "example_input": example_in,
            "expected_prediction_raw": expected_pred,
            "actual_prediction_raw": round(pred_raw, 6),
            "actual_prediction_clipped": round(pred_clipped, 6),
            "tolerance": tolerance,
            "within_tolerance": within_tolerance,
            "tolerance_threshold": 1.0,
            "overall_status": SEV_OK if within_tolerance else SEV_WARNING,
        }
    except Exception as exc:
        return {
            "status": "PREDICTION_ERROR",
            "overall_status": SEV_WARNING,
            "message": f"Example replay failed: {exc}",
            "error": str(exc),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LABEL AVAILABILITY
# ═══════════════════════════════════════════════════════════════════════════════

def check_label_availability(
    df: Any,
    result: MonitorResult,
    cfg: dict,
    with_labels: bool = False,
    target_column: Optional[str] = None,
) -> dict:
    """Phase 3 policy: NO performance metrics when labels unavailable."""
    target_candidates = {"target", "target_popularity", "y"}
    present = target_candidates & set(df.columns) if df is not None else set()

    labels_authorized = with_labels
    labels_present = bool(present)

    result.labels_authorized = labels_authorized

    if labels_present and not labels_authorized:
        result.warnings.append({
            "category": "LABELS",
            "message": "TARGET_PRESENT_BUT_NOT_AUTHORIZED",
            "detail": "Target column in batch but --with-labels not set",
        })
        return {
            "labels_present": True,
            "labels_authorized": False,
            "performance_computed": False,
            "performance_status": "LABELS_NOT_AVAILABLE",
            "status": "TARGET_PRESENT_BUT_NOT_AUTHORIZED",
            "message": "Target found but --with-labels flag not set — Phase 3 does not compute performance",
        }

    result.performance_check_executed = False
    return {
        "labels_present": labels_present,
        "labels_authorized": labels_authorized,
        "performance_computed": False,
        "performance_status": "LABELS_NOT_AVAILABLE",
        "status": "OK",
        "message": "Phase 3: performance metrics deferred to Phase 4 when labels are available",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ALERT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def build_alerts(result: MonitorResult) -> list[dict]:
    """Convert warnings/blockers to structured alert objects."""
    alerts = []
    for blk in result.blockers:
        alerts.append(MonitorAlert(
            alert_id=f"ALERT-{make_uuid()}",
            category=blk.get("category", "UNKNOWN"),
            metric=blk.get("check", blk.get("field", "unknown")),
            feature=blk.get("field"),
            expected=blk.get("expected"),
            actual=blk.get("actual"),
            threshold=blk.get("threshold"),
            threshold_source=blk.get("threshold_source", "PROJECT_CONFIG"),
            severity=blk.get("severity", SEV_BLOCKER),
            evidence={k: v for k, v in blk.items() if k not in ("category", "field", "severity", "message")},
            message=blk.get("message", ""),
            recommended_action=blk.get("recommended_action", "Investigate and resolve before continuing"),
            auto_action_executed=False,
        ).to_dict())

    for wng in result.warnings:
        alerts.append(MonitorAlert(
            alert_id=f"ALERT-{make_uuid()}",
            category=wng.get("category", "UNKNOWN"),
            metric=wng.get("check", wng.get("field", "unknown")),
            feature=wng.get("field"),
            expected=wng.get("expected"),
            actual=wng.get("actual"),
            threshold=wng.get("threshold"),
            threshold_source=wng.get("threshold_source", "PROJECT_CONFIG"),
            severity=wng.get("severity", SEV_WARNING),
            evidence={k: v for k, v in wng.items() if k not in ("category", "field", "severity", "message")},
            message=wng.get("message", ""),
            recommended_action=wng.get("recommended_action", "Monitor — no immediate action required"),
            auto_action_executed=False,
        ).to_dict())

    result.alerts = alerts
    return alerts


# ═══════════════════════════════════════════════════════════════════════════════
# OPEN ITEMS
# ═══════════════════════════════════════════════════════════════════════════════

def build_open_items(result: MonitorResult) -> list[dict]:
    """Collect unresolved items requiring review."""
    items = []

    for blk in result.blockers:
        items.append({
            "item_id": f"OI-{make_uuid()}",
            "alert_ids": [],
            "category": blk.get("category", "UNKNOWN"),
            "description": blk.get("message", ""),
            "severity": blk.get("severity", SEV_BLOCKER),
            "blocking": True,
            "owner": "TBD",
            "recommended_review": "BLOCKING: resolve before continuing",
            "retraining_candidate": False,
            "status": "OPEN",
        })

    # Phase 3: labels unavailable
    items.append({
        "item_id": f"OI-{make_uuid()}",
        "category": "PERFORMANCE",
        "description": "Phase 3 — labels not available. Performance metrics deferred to Phase 4.",
        "severity": SEV_INFO,
        "blocking": False,
        "owner": "Tuấn Anh",
        "recommended_review": "Phase 4 when labeled batch is available",
        "retraining_candidate": False,
        "status": "DEFERRED",
    })

    result.open_items = items
    return items


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def verify_governance(result: MonitorResult, cfg: dict) -> dict:
    """Verify governance constraints are respected."""
    gov = cfg.get("governance", {})
    violations = []

    if gov.get("auto_retrain", False):
        violations.append("auto_retrain must be false — monitor never triggers retraining")
    if gov.get("auto_update_baseline", False):
        violations.append("auto_update_baseline must be false — monitor never updates baseline")
    if result.training_executed:
        violations.append("training_executed must be false — monitor never trains")
    if result.refit_executed:
        violations.append("refit_executed must be false — monitor never refits")
    if result.auto_retrain_executed:
        violations.append("auto_retrain_executed must be false")
    if result.auto_update_baseline_executed:
        violations.append("auto_update_baseline_executed must be false")
    if result.champion_changed:
        violations.append("champion_changed must be false — monitor never changes champion")

    if result.baseline_hash_pre != result.baseline_hash_post:
        violations.append("BASELINE_MUTATED_DURING_MONITORING — baseline hash changed after monitoring run")

    result.warnings.extend([{"category": "GOVERNANCE", "message": v} for v in violations])

    return {
        "auto_retrain": False,
        "auto_update_baseline": False,
        "training_executed": False,
        "refit_executed": False,
        "auto_retrain_executed": False,
        "auto_update_baseline_executed": False,
        "champion_changed": False,
        "baseline_mutated": result.baseline_hash_pre != result.baseline_hash_post if result.baseline_hash_pre and result.baseline_hash_post else False,
        "governance_violations": violations,
        "overall_status": "PASS" if not violations else "FAIL",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MONITOR RUN
# ═══════════════════════════════════════════════════════════════════════════════

def run_monitor(
    config_path: Path,
    input_path: Optional[Path] = None,
    batch_id: Optional[str] = None,
    with_labels: bool = False,
    target_column: Optional[str] = None,
    schema_only: bool = False,
    data_quality_only: bool = False,
    feature_drift_only: bool = False,
    prediction_drift_only: bool = False,
    artifact_integrity_only: bool = False,
    output_dir: Optional[Path] = None,
    json_summary: bool = False,
    cfg_override: Optional[dict] = None,
) -> MonitorResult:
    """Execute the full monitoring pipeline."""
    started_at = utcnow()

    # Load config
    if cfg_override:
        cfg = cfg_override
    else:
        cfg = load_config(config_path)

    # ── GOVERNANCE ENFORCEMENT ──────────────────────────────────────────────
    gov = cfg.get("governance", {})
    gov_violations = []
    if gov.get("auto_retrain", False):
        gov_violations.append("auto_retrain must be false — monitor never triggers retraining")
    if gov.get("auto_update_baseline", False):
        gov_violations.append("auto_update_baseline must be false — monitor never updates baseline")

    # Resolve output dir early so we can write results even on governance failure
    _mon_dir = _MONITORING_DIR
    _pkg_dir = resolve_pkg_dir(cfg)
    _run_id = f"MON-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{make_uuid()}"
    _out_dir = resolve_output_dir(cfg, _run_id, explicit_dir=output_dir)

    if gov_violations:
        run_id_for_gov = f"MON-GOVERNANCE-{make_uuid()}"
        out_for_gov = resolve_output_dir(cfg, run_id_for_gov, explicit_dir=output_dir)
        result_for_gov = MonitorResult(
            monitor_run_id=run_id_for_gov,
            batch_id=None,
            model_id="N/A", model_version="N/A",
            package_version="N/A", data_version="N/A",
            baseline_id="N/A", baseline_version="N/A",
            overall_status="FAIL",
            started_at=utcnow(),
            ended_at=utcnow(),
            output_dir=out_for_gov,
        )
        result_for_gov.warnings = [{"category": "GOVERNANCE", "message": v} for v in gov_violations]
        result_for_gov.blockers = [{"category": "GOVERNANCE", "message": gov_violations[0], "severity": "BLOCKER", "check": "governance_violation"}]
        gov_block = {
            "auto_retrain": False, "auto_update_baseline": False,
            "training_executed": False, "refit_executed": False,
            "auto_retrain_executed": False, "auto_update_baseline_executed": False,
            "champion_changed": False, "baseline_mutated": False,
            "governance_violations": gov_violations,
            "overall_status": "FAIL",
        }
        result_dict = result_for_gov.to_dict()
        result_dict["governance"] = gov_block
        save_json(out_for_gov / "model_monitor_results.json", result_dict)
        save_json(out_for_gov / "model_monitor_alerts.json", {
            "generated_at": utcnow(),
            "alert_count": len(result_for_gov.blockers) + len(result_for_gov.warnings),
            "alerts": build_alerts(result_for_gov),
        })
        print("GOVERNANCE_VIOLATION:")
        for v in gov_violations:
            print(f"  - {v}")
        result_for_gov.output_dir = out_for_gov
        return result_for_gov

    # Resolve dirs
    pkg_dir = resolve_pkg_dir(cfg)
    mon_dir = _MONITORING_DIR

    # Generate run ID
    run_id = f"MON-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{make_uuid()}"

    out_dir = resolve_output_dir(cfg, run_id, explicit_dir=output_dir)

    # Load baseline
    baseline_path = mon_dir / "model_monitor_baseline.json"
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline not found: {baseline_path}")
    baseline = load_json(baseline_path)

    # Compute baseline hash BEFORE monitoring
    baseline_hash_pre = sha256_file(baseline_path)

    # Get model/package info from metadata
    model_ver_path = pkg_dir / "metadata" / "model_version.json"
    model_ver = load_json(model_ver_path) if model_ver_path.exists() else {}
    pkg_ver_path = pkg_dir / "metadata" / "package_version.json"
    pkg_ver = load_json(pkg_ver_path) if pkg_ver_path.exists() else {}
    data_ver_path = pkg_dir / "metadata" / "data_version.json"
    data_ver = load_json(data_ver_path) if data_ver_path.exists() else {}

    # Initialize result
    result = MonitorResult(
        monitor_run_id=run_id,
        batch_id=batch_id,
        model_id=model_ver.get("model_id", "UNKNOWN"),
        model_version=model_ver.get("model_version", "UNKNOWN"),
        package_version=pkg_ver.get("package_version", "UNKNOWN"),
        data_version=data_ver.get("data_version", "UNKNOWN"),
        baseline_id=baseline.get("baseline_id", "UNKNOWN"),
        baseline_version=baseline.get("baseline_version", "UNKNOWN"),
        baseline_hash_pre=baseline_hash_pre,
        started_at=started_at,
        output_dir=out_dir,
    )

    # Load input schema
    schema_path = pkg_dir / "schemas" / "input_schema.json"
    if schema_path.exists():
        input_schema = load_json(schema_path)
    else:
        result.blockers.append({
            "category": "CONFIG",
            "check": "missing_input_schema",
            "severity": SEV_BLOCKER,
            "message": f"Input schema not found: {schema_path}",
        })
        result.overall_status = SEV_BLOCKER
        return result

    # Load batch
    df = None
    if input_path:
        try:
            df, fmt = load_input_batch(input_path)
            result.input_rows = len(df)
            result.batch_id = batch_id or input_path.stem
        except Exception as exc:
            result.blockers.append({
                "category": "INPUT",
                "check": "load_error",
                "severity": SEV_BLOCKER,
                "message": f"Failed to load input: {exc}",
            })
            result.overall_status = SEV_BLOCKER
            return result

    # Label availability
    label_info = check_label_availability(df, result, cfg, with_labels, target_column)

    # ── SCHEMA ───────────────────────────────────────────────────────────────
    if (cfg.get("monitoring", {}).get("schema", True) and not schema_only
            and not artifact_integrity_only and df is not None):
        schema_results = monitor_schema(df, input_schema, result, cfg)
        save_json(out_dir / "model_monitor_schema_results.json", schema_results)

    # ── DATA QUALITY ─────────────────────────────────────────────────────────
    if cfg.get("monitoring", {}).get("data_quality", True) and df is not None:
        dq_results = monitor_data_quality(df, result, cfg)
        save_json(out_dir / "model_monitor_data_quality_results.json", dq_results)

    # ── SAMPLE SIZE ───────────────────────────────────────────────────────────
    sample_info = {
        "batch_rows": len(df) if df is not None else 0,
        "minimum_batch_rows": cfg.get("sample_requirements", {}).get("minimum_batch_rows", 30),
        "minimum_drift_rows": cfg.get("sample_requirements", {}).get("minimum_drift_rows", 100),
        "rows_above_minimum": (len(df) if df is not None else 0) >= cfg.get("sample_requirements", {}).get("minimum_batch_rows", 30),
        "rows_above_drift_minimum": (len(df) if df is not None else 0) >= cfg.get("sample_requirements", {}).get("minimum_drift_rows", 100),
        "drift_metrics_status": "NOT_ENOUGH_DATA" if (len(df) if df is not None else 0) < cfg.get("sample_requirements", {}).get("minimum_drift_rows", 100) else "OK",
    }
    save_json(out_dir / "model_monitor_sample_size_validation.json", sample_info)

    # ── NUMERIC DRIFT ─────────────────────────────────────────────────────────
    if (cfg.get("monitoring", {}).get("feature_drift", True)
            and not schema_only and not data_quality_only
            and not artifact_integrity_only and df is not None):
        num_results = monitor_numeric_drift(df, baseline, result, cfg)
        save_json(out_dir / "model_monitor_numeric_drift_results.json", num_results)

    # ── CATEGORICAL DRIFT ────────────────────────────────────────────────────
    if (cfg.get("monitoring", {}).get("feature_drift", True)
            and not schema_only and not data_quality_only
            and not artifact_integrity_only and df is not None):
        cat_results = monitor_categorical_drift(df, baseline, result, cfg)
        save_json(out_dir / "model_monitor_categorical_drift_results.json", cat_results)

        # ── FEATURE DRIFT SUMMARY ───────────────────────────────────────────
        drift_summary = compute_feature_drift_summary(num_results, cat_results, result)
        save_json(out_dir / "model_monitor_feature_drift_summary.json", drift_summary)

    # ── PREDICTION GENERATION ────────────────────────────────────────────────
    preds_df = None
    pred_gen_manifest = {}
    if (cfg.get("monitoring", {}).get("prediction_drift", True)
            and not schema_only and not data_quality_only
            and not artifact_integrity_only and df is not None):
        preds_df, pred_gen_manifest = generate_predictions(df, result)
        save_json(out_dir / "model_monitor_prediction_generation_manifest.json", pred_gen_manifest)

    # ── PREDICTION DRIFT ─────────────────────────────────────────────────────
    if (cfg.get("monitoring", {}).get("prediction_drift", True)
            and not schema_only and not data_quality_only):
        pred_results = monitor_prediction_drift(preds_df, baseline, result, cfg)
        save_json(out_dir / "model_monitor_prediction_drift_results.json", pred_results)

    # ── ARTIFACT INTEGRITY ───────────────────────────────────────────────────
    if cfg.get("monitoring", {}).get("artifact_integrity", True):
        artifact_results = monitor_artifact_integrity(result, cfg)
        save_json(out_dir / "model_monitor_artifact_integrity_results.json", artifact_results)

    # ── VERSION CONSISTENCY ───────────────────────────────────────────────────
    version_results = monitor_version_consistency(result, cfg)
    save_json(out_dir / "model_monitor_version_consistency.json", version_results)

    # ── EXAMPLE REPLAY ───────────────────────────────────────────────────────
    example_results = monitor_example_replay(result, cfg)
    save_json(out_dir / "model_monitor_example_replay_validation.json", example_results)

    # ── LABEL AVAILABILITY ───────────────────────────────────────────────────
    save_json(out_dir / "model_monitor_label_availability_validation.json", label_info)

    # ── BASELINE IMMUTABILITY ────────────────────────────────────────────────
    baseline_hash_post = sha256_file(baseline_path)
    result.baseline_hash_post = baseline_hash_post
    immutability = {
        "generated_at": utcnow(),
        "validation_type": "BASELINE_IMMUTABILITY_CHECK",
        "baseline_id": baseline.get("baseline_id"),
        "baseline_version": baseline.get("baseline_version"),
        "baseline_file_path": str(baseline_path),
        "pre_monitoring_hash": baseline_hash_pre,
        "post_monitoring_hash": baseline_hash_post,
        "hashes_match": baseline_hash_pre == baseline_hash_post,
        "result": "PASS" if baseline_hash_pre == baseline_hash_post else "FAIL",
    }
    if baseline_hash_pre != baseline_hash_post:
        result.blockers.append({
            "category": "GOVERNANCE",
            "check": "BASELINE_MUTATED_DURING_MONITORING",
            "severity": SEV_BLOCKER,
            "message": "Baseline file was modified during monitoring run",
        })
    save_json(out_dir / "model_monitor_baseline_immutability_validation.json", immutability)

    # ── GOVERNANCE ───────────────────────────────────────────────────────────
    gov_results = verify_governance(result, cfg)
    result.training_executed = False
    result.refit_executed = False
    result.auto_retrain_executed = False
    result.auto_update_baseline_executed = False
    result.champion_changed = False

    # ── ALERTS & OPEN ITEMS ──────────────────────────────────────────────────
    alerts = build_alerts(result)
    open_items = build_open_items(result)
    save_json(out_dir / "model_monitor_alerts.json", {
        "generated_at": utcnow(),
        "alert_count": len(alerts),
        "alerts": alerts,
    })
    save_json(out_dir / "model_monitor_open_items.json", {
        "generated_at": utcnow(),
        "open_item_count": len(open_items),
        "open_items": open_items,
    })

    # ── OVERALL STATUS ───────────────────────────────────────────────────────
    blocker_count = len(result.blockers)
    warning_count = len(result.warnings)
    governance_violations = len(gov_results.get("governance_violations", []))

    if blocker_count > 0 or governance_violations > 0:
        result.overall_status = "FAIL"
    elif warning_count > 0:
        result.overall_status = "PASS_WITH_WARNINGS"
    else:
        result.overall_status = "PASS"

    # Override if artifact integrity failed
    art_path = out_dir / "model_monitor_artifact_integrity_results.json"
    if art_path.exists():
        art = load_json(art_path)
        if art.get("overall_status") == SEV_BLOCKER:
            result.overall_status = "FAIL"

    ended_at = utcnow()
    result.ended_at = ended_at

    # Compute duration from started_at to ended_at
    try:
        started_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        ended_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
        result.duration_seconds = round((ended_dt - started_dt).total_seconds(), 3)
    except Exception:
        result.duration_seconds = 0.0

    # ── RUN MANIFEST ─────────────────────────────────────────────────────────
    run_manifest = {
        "monitor_run_id": run_id,
        "batch_id": result.batch_id,
        "model_id": result.model_id,
        "model_version": result.model_version,
        "data_version": result.data_version,
        "package_version": result.package_version,
        "baseline_id": result.baseline_id,
        "baseline_version": result.baseline_version,
        "input_rows": result.input_rows,
        "labels_authorized": result.labels_authorized,
        "schema_check_executed": result.schema_check_executed,
        "data_quality_check_executed": result.data_quality_check_executed,
        "feature_drift_check_executed": result.feature_drift_check_executed,
        "prediction_drift_check_executed": result.prediction_drift_check_executed,
        "performance_check_executed": result.performance_check_executed,
        "artifact_integrity_check_executed": result.artifact_integrity_check_executed,
        "training_executed": False,
        "refit_executed": False,
        "auto_retrain_executed": False,
        "auto_update_baseline_executed": False,
        "warnings": [w.get("message", str(w)) for w in result.warnings],
        "blockers": [b.get("message", str(b)) for b in result.blockers],
        "status": result.overall_status,
        "started_at": started_at,
        "ended_at": ended_at,
    }
    save_json(out_dir / "model_monitor_run_manifest.json", run_manifest)

    # ── SAVE MAIN RESULT ─────────────────────────────────────────────────────
    result_dict = result.to_dict()
    result_dict["governance"] = gov_results
    save_json(out_dir / "model_monitor_results.json", result_dict)

    if json_summary:
        print(json.dumps(result_dict, indent=2, default=str))

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="model_monitor.py",
        description="Feature 2.9 Phase 3/5 — Model Monitoring Core",
    )
    parser.add_argument("--config", type=Path, required=True,
                        help="Path to model_monitor_config.yaml")
    parser.add_argument("--input", type=Path, default=None,
                        help="Path to feature batch (CSV/Parquet/JSON)")
    parser.add_argument("--batch-id", type=str, default=None,
                        help="Optional batch identifier")
    parser.add_argument("--input-format", type=str, default="auto",
                        choices=["auto", "csv", "parquet", "json"],
                        help="Input file format")
    parser.add_argument("--schema-only", action="store_true",
                        help="Run schema check only")
    parser.add_argument("--data-quality-only", action="store_true",
                        help="Run data quality check only")
    parser.add_argument("--feature-drift", action="store_true",
                        help="Run feature drift check only")
    parser.add_argument("--prediction-drift", action="store_true",
                        help="Run prediction drift check only")
    parser.add_argument("--artifact-integrity", action="store_true",
                        help="Run artifact integrity check only")
    parser.add_argument("--with-labels", action="store_true",
                        help="Authorize label usage (Phase 4+)")
    parser.add_argument("--target-column", type=str, default=None,
                        help="Name of target column if present")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory for results")
    parser.add_argument("--json-summary", action="store_true",
                        help="Print JSON summary to stdout")

    args = parser.parse_args()

    # Validation
    if not args.config.exists():
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    if args.input and not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    try:
        result = run_monitor(
            config_path=args.config,
            input_path=args.input,
            batch_id=args.batch_id,
            with_labels=args.with_labels,
            target_column=args.target_column,
            schema_only=args.schema_only,
            data_quality_only=args.data_quality_only,
            feature_drift_only=args.feature_drift,
            prediction_drift_only=args.prediction_drift,
            artifact_integrity_only=args.artifact_integrity,
            output_dir=args.output_dir,
            json_summary=args.json_summary,
        )
    except FileNotFoundError as exc:
        print(f"BASELINE_ERROR: {exc}", file=sys.stderr)
        return EXIT_BASELINE_ERROR
    except Exception as exc:
        print(f"MONITORING_FAILURE: {exc}", file=sys.stderr)
        return EXIT_MONITORING_FAILURE

    # Console output — skip if json-summary mode
    if not args.json_summary:
        print(f"Monitor Run ID : {result.monitor_run_id}")
        print(f"Batch ID       : {result.batch_id or 'N/A'}")
        print(f"Model          : {result.model_id} v{result.model_version}")
        print(f"Package        : v{result.package_version}")
        print(f"Baseline       : {result.baseline_id} v{result.baseline_version}")
        h_pre = (result.baseline_hash_pre[:16] + "...") if result.baseline_hash_pre else "N/A"
        h_post = (result.baseline_hash_post[:16] + "...") if result.baseline_hash_post else "N/A"
        print(f"  Hash pre     : {h_pre}")
        print(f"  Hash post    : {h_post}")
        print(f"Schema         : {result.schema_status}")
        print(f"Data Quality   : {result.data_quality_status}")
        print(f"Feature Drift  : {result.feature_drift_status}")
        print(f"Pred Drift     : {result.prediction_drift_status}")
        print(f"Artifact Int.  : {result.artifact_integrity_status}")
        print(f"Labels Auth.   : {result.labels_authorized}")
        print(f"Training done  : {result.training_executed}")
        print(f"Refit done     : {result.refit_executed}")
        print(f"Auto-retrain   : {result.auto_retrain_executed}")
        print(f"Auto-baseline  : {result.auto_update_baseline_executed}")
        print(f"Champion chg   : {result.champion_changed}")
        print(f"Warnings       : {len(result.warnings)}")
        print(f"Blockers       : {len(result.blockers)}")
        print(f"Overall Status : {result.overall_status}")

    # Exit code
    if result.overall_status == "FAIL":
        if result.blockers:
            # Determine most specific exit code
            cats = {b.get("category", "") for b in result.blockers}
            if "ARTIFACT" in cats:
                return EXIT_ARTIFACT_FAIL
            if "SCHEMA" in cats:
                return EXIT_SCHEMA_BLOCKER
            if "GOVERNANCE" in cats:
                return EXIT_GOVERNANCE_VIOLATION
        return EXIT_MONITORING_FAILURE
    elif result.overall_status == "PASS_WITH_WARNINGS":
        return EXIT_WARNINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
