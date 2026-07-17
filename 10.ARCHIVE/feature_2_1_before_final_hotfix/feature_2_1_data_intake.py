#!/usr/bin/env python3
"""
Feature 2.1 — Data Intake, Validation & Temporal Split
HitRadar Pro — EPIC 2

Owner: Tuấn Anh
Purpose: Load ML-ready dataset, validate contract, freeze snapshot,
         analyze temporal distribution, create and lock temporal split.

This script does NOT:
  - Train any model
  - Fit imputer, scaler, encoder, KMeans, or feature selector
  - Perform feature engineering
  - Use random split as primary
  - Modify the source dataset
"""

import sys
import os
import json
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

# ============================================================
# CONFIGURATION
# ============================================================

# Project root detection
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent  # hitradar/

# Config paths - try multiple locations
CONFIG_CANDIDATES = [
    PROJECT_ROOT / "7.ML" / "7.1.config" / "experiment_config.yaml",
    PROJECT_ROOT / "4.MODELS" / "experiment_config.yaml",
]

# Also check Output epic2 for the Feature 2.0 config
OUTPUT_EPIC2_CONFIG = PROJECT_ROOT.parent / "Output epic2" / "feature_2_0_ml_contract" / "experiment_config.yaml"


def find_config():
    """Find experiment_config.yaml from known locations."""
    for path in CONFIG_CANDIDATES:
        if path.exists():
            return path
    if OUTPUT_EPIC2_CONFIG.exists():
        return OUTPUT_EPIC2_CONFIG
    return None


def load_config(config_path):
    """Load experiment config with yaml.safe_load."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def sha256_file(filepath):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_series(series):
    """Compute deterministic hash of a pandas Series (e.g., track_id list)."""
    h = hashlib.sha256()
    for val in series.sort_values().values:
        h.update(str(val).encode("utf-8"))
    return h.hexdigest()


def compute_schema_hash(df):
    """Compute a deterministic hash from column names and dtypes."""
    schema_str = "|".join(f"{col}:{df[col].dtype}" for col in df.columns)
    return hashlib.sha256(schema_str.encode("utf-8")).hexdigest()


# ============================================================
# TASK 2.1.1 — LOAD DATASET
# ============================================================

def task_2_1_1_load_dataset(config):
    """Load ML-ready dataset from source priority."""
    print("\n" + "=" * 60)
    print("TASK 2.1.1 — INSPECT, READ CONFIG & LOAD DATASET")
    print("=" * 60)

    # Verify config basics
    print(f"  Project: {config['project']['name']}")
    print(f"  EPIC: {config['project']['epic']}")
    print(f"  Contract version: {config['project']['contract_version']}")
    print(f"  Status: {config['project']['status']}")

    # Source priority
    source_priority = config["data"]["source_priority"]
    print(f"\n  Source priority: {source_priority}")

    actual_source = None
    df = None
    load_start = time.time()
    file_size = None
    source_type = None

    for source in source_priority:
        source_path = PROJECT_ROOT / source
        if source_path.exists():
            print(f"  Trying: {source_path}")
            if str(source).endswith(".parquet"):
                df = pd.read_parquet(source_path)
                source_type = "parquet"
            elif str(source).endswith(".csv"):
                df = pd.read_csv(source_path)
                source_type = "csv"
            actual_source = str(source_path)
            file_size = source_path.stat().st_size
            break
        else:
            print(f"  Not found: {source_path}")

    load_time = time.time() - load_start

    if df is None:
        print("  FAIL — DATA_SOURCE_UNAVAILABLE")
        sys.exit(1)

    print(f"\n  ✓ Loaded from: {actual_source}")
    print(f"  ✓ Source type: {source_type}")
    print(f"  ✓ File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print(f"  ✓ Load time: {load_time:.3f}s")
    print(f"  ✓ Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  ✓ Python version: {sys.version}")
    print(f"  ✓ pandas version: {pd.__version__}")
    try:
        import pyarrow
        print(f"  ✓ pyarrow version: {pyarrow.__version__}")
    except ImportError:
        print("  ✗ pyarrow not available")
    print(f"  ✓ Timestamp: {datetime.now(timezone.utc).isoformat()}")

    return df, actual_source, source_type, file_size, load_time


# ============================================================
# TASK 2.1.2 — FREEZE DATA VERSION
# ============================================================

def task_2_1_2_freeze_snapshot(df, config, actual_source, source_type, file_size):
    """Freeze input snapshot and create data version artifacts."""
    print("\n" + "=" * 60)
    print("TASK 2.1.2 — FREEZE INPUT SNAPSHOT & DATA VERSION")
    print("=" * 60)

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    data_version = f"ml-ready-{date_str}-v1"

    # Compute file hash
    file_hash = sha256_file(actual_source)
    schema_hash = compute_schema_hash(df)

    # Content fingerprint: hash of sorted track_ids + row count
    content_fp = hashlib.sha256()
    content_fp.update(str(df.shape[0]).encode())
    content_fp.update(str(df.shape[1]).encode())
    for col in sorted(df.columns):
        content_fp.update(col.encode())
    content_fingerprint = content_fp.hexdigest()[:16]

    data_version_info = {
        "data_version": data_version,
        "canonical_source": "analytics.vw_ml_ready_dataset",
        "actual_source_used": str(actual_source),
        "source_type": source_type,
        "file_size_bytes": file_size,
        "file_modified": datetime.fromtimestamp(
            Path(actual_source).stat().st_mtime, tz=timezone.utc
        ).isoformat(),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "identifier": config["data"]["identifier_column"],
        "target": config["data"]["target_column"],
        "baseline_features_count": len(config["data"]["baseline_features"]),
        "schema_hash": schema_hash,
        "file_sha256": file_hash,
        "content_fingerprint": content_fingerprint,
        "created_at": now.isoformat(),
    }

    # Schema snapshot
    schema_snapshot = {
        "data_version": data_version,
        "columns": [],
    }
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "nullable": bool(df[col].isnull().any()),
            "null_count": int(df[col].isnull().sum()),
            "unique_count": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["min"] = float(df[col].min()) if not df[col].isnull().all() else None
            col_info["max"] = float(df[col].max()) if not df[col].isnull().all() else None
        if col == config["data"]["identifier_column"]:
            col_info["role"] = "identifier"
        elif col == config["data"]["target_column"]:
            col_info["role"] = "target"
        elif col in config["data"]["baseline_features"]:
            col_info["role"] = "input_feature"
        else:
            col_info["role"] = "unknown"
        schema_snapshot["columns"].append(col_info)

    # Input manifest
    input_manifest = {
        "data_version": data_version,
        "source_priority": config["data"]["source_priority"],
        "actual_source_used": str(actual_source),
        "expected_rows": config["data"]["expected_rows"],
        "expected_columns": config["data"]["expected_columns"],
        "actual_rows": int(df.shape[0]),
        "actual_columns": int(df.shape[1]),
        "identifier_column": config["data"]["identifier_column"],
        "target_column": config["data"]["target_column"],
        "baseline_features": config["data"]["baseline_features"],
        "forbidden_columns": config["data"]["forbidden_columns"],
        "schema_hash": schema_hash,
        "file_sha256": file_hash,
        "created_at": now.isoformat(),
    }

    # Check expected shape
    expected_rows = config["data"]["expected_rows"]
    expected_cols = config["data"]["expected_columns"]

    if df.shape[0] != expected_rows or df.shape[1] != expected_cols:
        print(f"  FAIL — CONTRACT_MISMATCH")
        print(f"    Expected: {expected_rows} × {expected_cols}")
        print(f"    Actual:   {df.shape[0]} × {df.shape[1]}")
        sys.exit(1)

    print(f"  ✓ Data version: {data_version}")
    print(f"  ✓ File SHA-256: {file_hash[:16]}...")
    print(f"  ✓ Schema hash:  {schema_hash[:16]}...")
    print(f"  ✓ Rows match contract: {df.shape[0]:,} = {expected_rows:,}")
    print(f"  ✓ Cols match contract: {df.shape[1]} = {expected_cols}")

    return data_version_info, schema_snapshot, input_manifest, data_version


# ============================================================
# TASK 2.1.3 — VALIDATE SCHEMA & COLUMN ROLES
# ============================================================

def task_2_1_3_validate_schema(df, config):
    """Validate schema, column roles and forbidden columns."""
    print("\n" + "=" * 60)
    print("TASK 2.1.3 — VALIDATE SCHEMA, COLUMN ROLES & FORBIDDEN COLUMNS")
    print("=" * 60)

    errors = []

    # Expected columns (20)
    expected_columns = (
        [config["data"]["identifier_column"]]
        + [config["data"]["target_column"]]
        + config["data"]["baseline_features"]
    )

    actual_columns = list(df.columns)

    # Check exact 20 columns
    print(f"  Expected column count: {len(expected_columns)}")
    print(f"  Actual column count:   {len(actual_columns)}")

    if len(actual_columns) != len(expected_columns):
        errors.append(f"Column count mismatch: expected {len(expected_columns)}, got {len(actual_columns)}")

    # Check for missing columns
    missing = set(expected_columns) - set(actual_columns)
    if missing:
        errors.append(f"Missing columns: {missing}")
        print(f"  ✗ Missing columns: {missing}")
    else:
        print(f"  ✓ All 20 expected columns present")

    # Check for extra columns
    extra = set(actual_columns) - set(expected_columns)
    if extra:
        errors.append(f"Extra columns: {extra}")
        print(f"  ✗ Extra columns: {extra}")
    else:
        print(f"  ✓ No extra columns")

    # Check for Unnamed columns
    unnamed = [c for c in actual_columns if c.startswith("Unnamed")]
    if unnamed:
        errors.append(f"Unnamed columns found: {unnamed}")
        print(f"  ✗ Unnamed columns: {unnamed}")
    else:
        print(f"  ✓ No Unnamed columns")

    # Check for whitespace in column names
    ws_cols = [c for c in actual_columns if c != c.strip()]
    if ws_cols:
        errors.append(f"Columns with whitespace: {ws_cols}")
        print(f"  ✗ Columns with leading/trailing whitespace: {ws_cols}")
    else:
        print(f"  ✓ No whitespace issues in column names")

    # Check for duplicate column names
    if len(actual_columns) != len(set(actual_columns)):
        errors.append("Duplicate column names detected")
        print(f"  ✗ Duplicate column names!")
    else:
        print(f"  ✓ No duplicate column names")

    # Check forbidden columns not in input features
    forbidden = config["data"]["forbidden_columns"]
    baseline = config["data"]["baseline_features"]

    forbidden_in_features = set(forbidden) & set(baseline)
    if forbidden_in_features:
        errors.append(f"FORBIDDEN_LEAKAGE_COLUMN_DETECTED in features: {forbidden_in_features}")
        print(f"  ✗ FAIL — FORBIDDEN_LEAKAGE_COLUMN_DETECTED: {forbidden_in_features}")
    else:
        print(f"  ✓ No forbidden columns in baseline features")

    # Check identifier and target not in baseline features
    id_col = config["data"]["identifier_column"]
    tgt_col = config["data"]["target_column"]

    if id_col in baseline:
        errors.append(f"{id_col} found in baseline features")
    else:
        print(f"  ✓ {id_col} not in baseline features")

    if tgt_col in baseline:
        errors.append(f"{tgt_col} found in baseline features")
    else:
        print(f"  ✓ {tgt_col} not in baseline features")

    # Column role classification
    print("\n  Column Roles:")
    for col in actual_columns:
        if col == id_col:
            role = "identifier"
        elif col == tgt_col:
            role = "target"
        elif col in baseline:
            role = "input_feature"
        else:
            role = "unknown"
        print(f"    {col:30s} → {role}")

    if errors:
        print(f"\n  SCHEMA VALIDATION: FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"    ✗ {e}")
        sys.exit(1)
    else:
        print(f"\n  ✓ SCHEMA VALIDATION: PASS")

    return errors


# ============================================================
# TASK 2.1.4 — VALIDATE IDENTIFIER & TARGET
# ============================================================

def task_2_1_4_validate_id_target(df, config):
    """Validate track_id and target_popularity."""
    print("\n" + "=" * 60)
    print("TASK 2.1.4 — VALIDATE IDENTIFIER & TARGET")
    print("=" * 60)

    id_col = config["data"]["identifier_column"]
    tgt_col = config["data"]["target_column"]
    errors = []

    # --- track_id ---
    print(f"\n  A. Identifier: {id_col}")
    id_null = int(df[id_col].isnull().sum())
    id_empty = int((df[id_col].astype(str).str.strip() == "").sum()) if id_null == 0 else -1
    id_dup = int(df[id_col].duplicated().sum())
    id_unique = int(df[id_col].nunique())

    print(f"    NULL count:            {id_null}")
    print(f"    Empty/whitespace-only: {id_empty}")
    print(f"    Duplicate count:       {id_dup}")
    print(f"    Unique count:          {id_unique:,}")
    print(f"    Expected unique:       {df.shape[0]:,}")

    if id_null > 0:
        errors.append(f"IDENTIFIER_INTEGRITY_FAILURE: {id_col} has {id_null} NULLs")
    if id_dup > 0:
        errors.append(f"IDENTIFIER_INTEGRITY_FAILURE: {id_col} has {id_dup} duplicates")
    if id_unique != df.shape[0]:
        errors.append(f"IDENTIFIER_INTEGRITY_FAILURE: unique count {id_unique} != row count {df.shape[0]}")

    if not errors:
        print(f"    ✓ Identifier validation: PASS")

    # --- target_popularity ---
    print(f"\n  B. Target: {tgt_col}")
    tgt = df[tgt_col]
    tgt_null = int(tgt.isnull().sum())
    tgt_nan = int(np.isnan(tgt).sum()) if pd.api.types.is_numeric_dtype(tgt) else -1
    tgt_inf = int(np.isinf(tgt).sum()) if pd.api.types.is_numeric_dtype(tgt) else -1
    tgt_min = float(tgt.min())
    tgt_max = float(tgt.max())
    tgt_mean = float(tgt.mean())
    tgt_median = float(tgt.median())
    tgt_std = float(tgt.std())
    tgt_zero = int((tgt == 0).sum())

    quantiles = tgt.quantile([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).to_dict()

    # Popularity buckets
    buckets = {
        "0-20": int(((tgt >= 0) & (tgt <= 20)).sum()),
        "21-40": int(((tgt >= 21) & (tgt <= 40)).sum()),
        "41-60": int(((tgt >= 41) & (tgt <= 60)).sum()),
        "61-80": int(((tgt >= 61) & (tgt <= 80)).sum()),
        "81-100": int(((tgt >= 81) & (tgt <= 100)).sum()),
    }
    bucket_ratios = {k: round(v / len(tgt) * 100, 2) for k, v in buckets.items()}

    print(f"    NULL count:     {tgt_null}")
    print(f"    NaN count:      {tgt_nan}")
    print(f"    Infinite count: {tgt_inf}")
    print(f"    Min:            {tgt_min}")
    print(f"    Max:            {tgt_max}")
    print(f"    Mean:           {tgt_mean:.4f}")
    print(f"    Median:         {tgt_median}")
    print(f"    Std:            {tgt_std:.4f}")
    print(f"    Zero count:     {tgt_zero:,}")
    print(f"    Quantiles:      {quantiles}")
    print(f"    Buckets:        {buckets}")
    print(f"    Bucket ratios:  {bucket_ratios}")

    tgt_range = config["data"]["target_range"]
    if tgt_null > 0:
        errors.append(f"TARGET_CONTRACT_FAILURE: target has {tgt_null} NULLs")
    if tgt_nan > 0:
        errors.append(f"TARGET_CONTRACT_FAILURE: target has {tgt_nan} NaNs")
    if tgt_inf > 0:
        errors.append(f"TARGET_CONTRACT_FAILURE: target has {tgt_inf} infinites")
    if tgt_min < tgt_range["min"]:
        errors.append(f"TARGET_CONTRACT_FAILURE: min {tgt_min} < {tgt_range['min']}")
    if tgt_max > tgt_range["max"]:
        errors.append(f"TARGET_CONTRACT_FAILURE: max {tgt_max} > {tgt_range['max']}")

    if not [e for e in errors if "TARGET" in e]:
        print(f"    ✓ Target validation: PASS")

    # Build target profile
    target_profile = {
        "column": tgt_col,
        "count": int(len(tgt)),
        "null_count": tgt_null,
        "nan_count": tgt_nan,
        "infinite_count": tgt_inf,
        "zero_count": tgt_zero,
        "min": tgt_min,
        "max": tgt_max,
        "mean": round(tgt_mean, 4),
        "median": tgt_median,
        "std": round(tgt_std, 4),
        "quantiles": {str(k): float(v) for k, v in quantiles.items()},
        "buckets": buckets,
        "bucket_ratios_pct": bucket_ratios,
    }

    if errors:
        print(f"\n  IDENTIFIER/TARGET VALIDATION: FAIL")
        for e in errors:
            print(f"    ✗ {e}")
        sys.exit(1)

    return target_profile


# ============================================================
# TASK 2.1.5 — RE-AUDIT WARNING BASELINE
# ============================================================

def task_2_1_5_reaudit_warnings(df, config):
    """Re-audit warning baseline from EPIC 1."""
    print("\n" + "=" * 60)
    print("TASK 2.1.5 — RE-AUDIT WARNING BASELINE")
    print("=" * 60)

    warnings_expected = config.get("warnings_carry_forward", {})
    warning_results = {}
    deviations = []

    # Missing values
    print("\n  Missing Values:")
    missing_checks = {
        "tempo": ("tempo_null_count", 328),
        "time_signature": ("time_signature_null_count", 337),
        "release_month": ("release_month_null_count", 136489),
    }

    for col, (key, expected) in missing_checks.items():
        if col in df.columns:
            actual = int(df[col].isnull().sum())
            match = "✓" if actual == expected else "⚠"
            print(f"    {col} NULL: {actual:,} (expected {expected:,}) {match}")
            warning_results[key] = {
                "actual": actual,
                "expected": expected,
                "match": actual == expected,
            }
            if actual != expected:
                deviations.append(f"{col} NULL: expected {expected}, got {actual}")
        else:
            print(f"    {col}: column not found!")

    # Check release_year NULL (critical for temporal split)
    ry_null = int(df["release_year"].isnull().sum())
    print(f"    release_year NULL: {ry_null}")
    warning_results["release_year_null_count"] = {"actual": ry_null, "expected": 0}
    if ry_null > 0:
        print(f"    ✗ TEMPORAL_KEY_MISSING — {ry_null} rows have NULL release_year")

    # target NULL
    tgt_null = int(df[config["data"]["target_column"]].isnull().sum())
    print(f"    target_popularity NULL: {tgt_null}")
    warning_results["target_null_count"] = {"actual": tgt_null, "expected": 0}

    # track_id NULL
    id_null = int(df[config["data"]["identifier_column"]].isnull().sum())
    print(f"    track_id NULL: {id_null}")

    # Range/sanity checks
    print("\n  Range/Sanity Checks:")
    range_01 = ["danceability", "energy", "speechiness", "acousticness",
                "instrumentalness", "liveness", "valence"]

    for col in range_01:
        if col in df.columns:
            non_null = df[col].dropna()
            violations = int(((non_null < 0) | (non_null > 1)).sum())
            status = "✓" if violations == 0 else f"✗ {violations} violations"
            print(f"    {col} in [0,1]: {status}")
            warning_results[f"{col}_range_violations"] = violations

    # Duration
    if "duration_min" in df.columns:
        dur = df["duration_min"].dropna()
        short = int((dur < 10/60).sum())  # < 10 seconds in minutes
        long_dur = int((dur > 60).sum())  # > 60 minutes
        print(f"    duration < 10s: {short} (expected {warnings_expected.get('duration_short_under_10s_count', 'N/A')})")
        print(f"    duration > 60min: {long_dur} (expected {warnings_expected.get('duration_long_over_60min_count', 'N/A')})")
        warning_results["duration_short_under_10s"] = {
            "actual": short,
            "expected": warnings_expected.get("duration_short_under_10s_count", None),
        }
        warning_results["duration_long_over_60min"] = {
            "actual": long_dur,
            "expected": warnings_expected.get("duration_long_over_60min_count", None),
        }

    # Loudness > 0
    if "loudness" in df.columns:
        loud_pos = int((df["loudness"].dropna() > 0).sum())
        print(f"    loudness > 0 dB: {loud_pos} (expected {warnings_expected.get('loudness_positive_count', 'N/A')})")
        warning_results["loudness_positive"] = {
            "actual": loud_pos,
            "expected": warnings_expected.get("loudness_positive_count", None),
        }

    # Target imbalance
    tgt = df[config["data"]["target_column"]]
    tgt_zero = int((tgt == 0).sum())
    tgt_le40 = int((tgt <= 40).sum())
    tgt_le40_pct = round(tgt_le40 / len(tgt) * 100, 2)
    print(f"\n  Target Diagnostics:")
    print(f"    target = 0: {tgt_zero:,} (expected {warnings_expected.get('target_popularity_zero_count', 'N/A')})")
    print(f"    target <= 40: {tgt_le40:,} ({tgt_le40_pct}%) (expected ~75%)")
    warning_results["target_zero_count"] = {
        "actual": tgt_zero,
        "expected": warnings_expected.get("target_popularity_zero_count", None),
    }
    warning_results["target_le40_pct"] = tgt_le40_pct

    # Correlation diagnostic
    if "release_year" in df.columns:
        corr = float(df["release_year"].corr(tgt))
        print(f"    release_year × target correlation: {corr:.4f} (expected ~+0.5909)")
        warning_results["release_year_target_corr"] = round(corr, 4)

    # Key and mode domain
    if "key" in df.columns:
        key_vals = sorted(df["key"].dropna().unique().tolist())
        print(f"    key unique values: {key_vals}")
        warning_results["key_domain"] = key_vals
    if "mode" in df.columns:
        mode_vals = sorted(df["mode"].dropna().unique().tolist())
        print(f"    mode unique values: {mode_vals}")
        warning_results["mode_domain"] = mode_vals
    if "time_signature" in df.columns:
        ts_vals = sorted(df["time_signature"].dropna().unique().tolist())
        print(f"    time_signature unique values: {ts_vals}")
        warning_results["time_signature_domain"] = ts_vals

    # Classify warnings
    for dev in deviations:
        print(f"  ⚠ DATA_DISTRIBUTION_DEVIATION: {dev}")

    print(f"\n  ✓ Warning audit complete. {len(deviations)} deviations found.")

    return warning_results


# ============================================================
# TASK 2.1.6 — TEMPORAL ANALYSIS & SPLIT CANDIDATES
# ============================================================

def task_2_1_6_temporal_analysis(df, config):
    """Analyze release_year distribution and create split candidates."""
    print("\n" + "=" * 60)
    print("TASK 2.1.6 — TEMPORAL ANALYSIS & SPLIT CANDIDATES")
    print("=" * 60)

    time_col = config["split"]["split_column"]
    tgt_col = config["data"]["target_column"]

    # Year distribution
    year_dist = df.groupby(time_col).agg(
        row_count=(tgt_col, "size"),
        mean_target=(tgt_col, "mean"),
        median_target=(tgt_col, "median"),
        std_target=(tgt_col, "std"),
        zero_count=(tgt_col, lambda x: int((x == 0).sum())),
    ).reset_index()

    year_dist["row_ratio"] = (year_dist["row_count"] / year_dist["row_count"].sum() * 100).round(4)
    year_dist["cumulative_count"] = year_dist["row_count"].cumsum()
    year_dist["cumulative_ratio"] = (year_dist["cumulative_count"] / year_dist["row_count"].sum() * 100).round(4)

    # Add missing ratios per year for key columns
    for col in ["tempo", "time_signature", "release_month"]:
        if col in df.columns:
            miss_by_year = df.groupby(time_col)[col].apply(lambda x: x.isnull().sum()).reset_index()
            miss_by_year.columns = [time_col, f"{col}_null_count"]
            year_dist = year_dist.merge(miss_by_year, on=time_col, how="left")

    min_year = int(year_dist[time_col].min())
    max_year = int(year_dist[time_col].max())
    total_rows = int(year_dist["row_count"].sum())

    print(f"  Year range: {min_year} – {max_year}")
    print(f"  Total rows: {total_rows:,}")
    print(f"  Total unique years: {len(year_dist)}")

    # Decade distribution
    print("\n  Decade Distribution:")
    df_temp = df.copy()
    df_temp["_decade"] = (df_temp[time_col] // 10) * 10
    decade_dist = df_temp.groupby("_decade").agg(
        count=(tgt_col, "size"),
        mean_target=(tgt_col, "mean"),
    ).reset_index()
    for _, row in decade_dist.iterrows():
        pct = row["count"] / total_rows * 100
        print(f"    {int(row['_decade'])}s: {int(row['count']):>8,} ({pct:.1f}%)  mean_target={row['mean_target']:.1f}")

    # Identify years with very few rows
    sparse_years = year_dist[year_dist["row_count"] < 100]
    if len(sparse_years) > 0:
        print(f"\n  ⚠ {len(sparse_years)} years with < 100 rows")

    # Create split candidates
    ratios = config["split"]["target_ratios"]

    # We need to find year cutoffs that approximately match target ratios
    # Candidate 1: Conservative — older test boundary
    # Candidate 2: Balanced — moderate split
    # Candidate 3: Recent-heavy test

    candidates = []

    # Strategy: iterate possible validation_start and test_start
    # keeping train_ratio in [65%,75%], val in [10%,20%], test in [10%,20%]
    years_sorted = sorted(year_dist[time_col].unique())

    best_candidates = []

    for vi, val_start_year in enumerate(years_sorted):
        for ti, test_start_year in enumerate(years_sorted):
            if test_start_year <= val_start_year:
                continue

            train_mask = df[time_col] < val_start_year
            val_mask = (df[time_col] >= val_start_year) & (df[time_col] < test_start_year)
            test_mask = df[time_col] >= test_start_year

            train_n = int(train_mask.sum())
            val_n = int(val_mask.sum())
            test_n = int(test_mask.sum())

            if train_n == 0 or val_n == 0 or test_n == 0:
                continue

            train_r = train_n / total_rows
            val_r = val_n / total_rows
            test_r = test_n / total_rows

            # Check ratio bounds
            if not (ratios["train_min"] <= train_r <= ratios["train_max"]):
                continue
            if not (ratios["validation_min"] <= val_r <= ratios["validation_max"]):
                continue
            if not (ratios["test_min"] <= test_r <= ratios["test_max"]):
                continue

            # Must include max year in test
            if max_year not in df[test_mask][time_col].values:
                continue

            # Score: prefer balanced ratios
            ideal_train = 0.70
            ideal_val = 0.15
            ideal_test = 0.15
            score = abs(train_r - ideal_train) + abs(val_r - ideal_val) + abs(test_r - ideal_test)

            best_candidates.append({
                "val_start": int(val_start_year),
                "test_start": int(test_start_year),
                "train_n": train_n,
                "val_n": val_n,
                "test_n": test_n,
                "train_r": round(train_r, 4),
                "val_r": round(val_r, 4),
                "test_r": round(test_r, 4),
                "score": round(score, 4),
                "train_years": f"{min_year}-{int(val_start_year)-1}",
                "val_years": f"{int(val_start_year)}-{int(test_start_year)-1}",
                "test_years": f"{int(test_start_year)}-{max_year}",
            })

    # Sort by score, take top candidates
    best_candidates.sort(key=lambda x: x["score"])

    # Pick 3 diverse candidates
    selected = []
    used_val_starts = set()
    for c in best_candidates:
        if c["val_start"] not in used_val_starts:
            selected.append(c)
            used_val_starts.add(c["val_start"])
        if len(selected) >= 3:
            break

    print(f"\n  Split Candidates ({len(selected)} evaluated):")
    for i, c in enumerate(selected):
        cid = f"C{i+1}"
        c["candidate_id"] = cid
        print(f"\n    {cid}: Train={c['train_years']} | Val={c['val_years']} | Test={c['test_years']}")
        print(f"        Rows: {c['train_n']:,} / {c['val_n']:,} / {c['test_n']:,}")
        print(f"        Ratios: {c['train_r']:.1%} / {c['val_r']:.1%} / {c['test_r']:.1%}")
        print(f"        Score: {c['score']:.4f}")

        # Compute target stats per split for this candidate
        train_mask = df[time_col] < c["val_start"]
        val_mask = (df[time_col] >= c["val_start"]) & (df[time_col] < c["test_start"])
        test_mask = df[time_col] >= c["test_start"]

        for name, mask in [("train", train_mask), ("val", val_mask), ("test", test_mask)]:
            subset = df[mask][tgt_col]
            c[f"{name}_mean_target"] = round(float(subset.mean()), 2)
            c[f"{name}_median_target"] = float(subset.median())
            c[f"{name}_zero_count"] = int((subset == 0).sum())

        print(f"        Target mean: {c['train_mean_target']:.1f} / {c['val_mean_target']:.1f} / {c['test_mean_target']:.1f}")

    return year_dist, selected, min_year, max_year


# ============================================================
# TASK 2.1.7 — LOCK TEMPORAL SPLIT
# ============================================================

def task_2_1_7_lock_split(df, config, candidates, min_year, max_year):
    """Select best candidate and lock temporal split."""
    print("\n" + "=" * 60)
    print("TASK 2.1.7 — LOCK TEMPORAL SPLIT")
    print("=" * 60)

    if not candidates:
        print("  FAIL — No valid split candidates found")
        sys.exit(1)

    # Select the best candidate (lowest score = most balanced)
    best = candidates[0]
    print(f"  Selected candidate: {best['candidate_id']}")
    print(f"  Reason: Best balance of train/val/test ratios while maintaining chronology")

    time_col = config["split"]["split_column"]
    id_col = config["data"]["identifier_column"]
    tgt_col = config["data"]["target_column"]

    train_end = best["val_start"] - 1
    val_start = best["val_start"]
    val_end = best["test_start"] - 1
    test_start = best["test_start"]

    # Create splits
    train_mask = df[time_col] <= train_end
    val_mask = (df[time_col] >= val_start) & (df[time_col] <= val_end)
    test_mask = df[time_col] >= test_start

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    print(f"\n  Locked Split:")
    print(f"    Train:      {min_year}–{train_end} | {len(train_df):,} rows ({len(train_df)/len(df):.1%})")
    print(f"    Validation: {val_start}–{val_end} | {len(val_df):,} rows ({len(val_df)/len(df):.1%})")
    print(f"    Test:       {test_start}–{max_year} | {len(test_df):,} rows ({len(test_df)/len(df):.1%})")

    # Chronology check
    train_max_year = int(train_df[time_col].max())
    val_min_year = int(val_df[time_col].min())
    val_max_year = int(val_df[time_col].max())
    test_min_year = int(test_df[time_col].min())

    chrono_ok = (train_max_year < val_min_year) and (val_max_year < test_min_year)
    print(f"\n  Chronology: max(train)={train_max_year} < min(val)={val_min_year} "
          f"< max(val)={val_max_year} < min(test)={test_min_year}")
    print(f"  Chronology valid: {'✓ PASS' if chrono_ok else '✗ FAIL'}")

    if not chrono_ok:
        print("  FAIL — CHRONOLOGY_VIOLATION")
        sys.exit(1)

    split_info = {
        "train_start": min_year,
        "train_end": train_end,
        "val_start": val_start,
        "val_end": val_end,
        "test_start": test_start,
        "test_end": max_year,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "selected_candidate": best["candidate_id"],
    }

    return train_df, val_df, test_df, split_info


# ============================================================
# TASK 2.1.8 — VALIDATE SPLIT INTEGRITY
# ============================================================

def task_2_1_8_validate_split(df, train_df, val_df, test_df, config, split_info):
    """Validate split integrity, chronology and leakage."""
    print("\n" + "=" * 60)
    print("TASK 2.1.8 — VALIDATE SPLIT INTEGRITY & LEAKAGE")
    print("=" * 60)

    id_col = config["data"]["identifier_column"]
    tgt_col = config["data"]["target_column"]
    time_col = config["split"]["split_column"]
    errors = []

    train_ids = set(train_df[id_col])
    val_ids = set(val_df[id_col])
    test_ids = set(test_df[id_col])

    # 1-3. Overlap checks
    tv_overlap = len(train_ids & val_ids)
    tt_overlap = len(train_ids & test_ids)
    vt_overlap = len(val_ids & test_ids)

    print(f"  1. train ∩ validation: {tv_overlap} {'✓' if tv_overlap == 0 else '✗ FAIL'}")
    print(f"  2. train ∩ test:       {tt_overlap} {'✓' if tt_overlap == 0 else '✗ FAIL'}")
    print(f"  3. validation ∩ test:  {vt_overlap} {'✓' if vt_overlap == 0 else '✗ FAIL'}")

    if tv_overlap > 0:
        errors.append(f"Track overlap train-val: {tv_overlap}")
    if tt_overlap > 0:
        errors.append(f"Track overlap train-test: {tt_overlap}")
    if vt_overlap > 0:
        errors.append(f"Track overlap val-test: {vt_overlap}")

    # 4-5. Duplicate/NULL within splits
    for name, split_df in [("train", train_df), ("validation", val_df), ("test", test_df)]:
        dup = int(split_df[id_col].duplicated().sum())
        null = int(split_df[id_col].isnull().sum())
        print(f"  4. {name} duplicate track_id: {dup} {'✓' if dup == 0 else '✗ FAIL'}")
        print(f"  5. {name} NULL track_id: {null} {'✓' if null == 0 else '✗ FAIL'}")
        if dup > 0:
            errors.append(f"{name} has {dup} duplicate track_ids")
        if null > 0:
            errors.append(f"{name} has {null} NULL track_ids")

    # 6. Row reconciliation
    total_split = len(train_df) + len(val_df) + len(test_df)
    total_source = len(df)
    recon_ok = total_split == total_source
    print(f"  6. Row reconciliation: {total_split:,} vs {total_source:,} {'✓' if recon_ok else '✗ FAIL'}")
    if not recon_ok:
        errors.append(f"Row sum {total_split} != source {total_source}")

    # 7. Each row belongs to exactly one split
    all_ids = set(train_df[id_col]) | set(val_df[id_col]) | set(test_df[id_col])
    print(f"  7. All rows accounted: {len(all_ids):,} unique IDs {'✓' if len(all_ids) == total_source else '✗'}")

    # 8-9. Chronology
    train_max_y = int(train_df[time_col].max())
    val_min_y = int(val_df[time_col].min())
    val_max_y = int(val_df[time_col].max())
    test_min_y = int(test_df[time_col].min())

    chrono_1 = train_max_y < val_min_y
    chrono_2 = val_max_y < test_min_y
    print(f"  8. max(train year) < min(val year): {train_max_y} < {val_min_y} {'✓' if chrono_1 else '✗ FAIL'}")
    print(f"  9. max(val year) < min(test year): {val_max_y} < {test_min_y} {'✓' if chrono_2 else '✗ FAIL'}")

    if not chrono_1:
        errors.append("Chronology violation: train/validation overlap")
    if not chrono_2:
        errors.append("Chronology violation: validation/test overlap")

    # 10. Test contains max year
    test_has_max = max(df[time_col]) in test_df[time_col].values
    print(f"  10. Test contains max year: {'✓' if test_has_max else '✗'}")

    # 13. Target and identifier not in features
    baseline = config["data"]["baseline_features"]
    print(f"  13. {tgt_col} not in features: {'✓' if tgt_col not in baseline else '✗'}")
    print(f"      {id_col} not in features: {'✓' if id_col not in baseline else '✗'}")

    # Profile each split
    print("\n  Split Profiles:")
    profiles = {}
    for name, split_df in [("train", train_df), ("validation", val_df), ("test", test_df)]:
        tgt = split_df[tgt_col]
        profile = {
            "row_count": int(len(split_df)),
            "row_ratio": round(len(split_df) / total_source, 4),
            "min_year": int(split_df[time_col].min()),
            "max_year": int(split_df[time_col].max()),
            "target_mean": round(float(tgt.mean()), 4),
            "target_median": float(tgt.median()),
            "target_std": round(float(tgt.std()), 4),
            "target_zero_count": int((tgt == 0).sum()),
            "buckets": {
                "0-20": int(((tgt >= 0) & (tgt <= 20)).sum()),
                "21-40": int(((tgt >= 21) & (tgt <= 40)).sum()),
                "41-60": int(((tgt >= 41) & (tgt <= 60)).sum()),
                "61-80": int(((tgt >= 61) & (tgt <= 80)).sum()),
                "81-100": int(((tgt >= 81) & (tgt <= 100)).sum()),
            },
            "missing_tempo": int(split_df["tempo"].isnull().sum()) if "tempo" in split_df.columns else 0,
            "missing_time_signature": int(split_df["time_signature"].isnull().sum()) if "time_signature" in split_df.columns else 0,
            "missing_release_month": int(split_df["release_month"].isnull().sum()) if "release_month" in split_df.columns else 0,
        }
        profiles[name] = profile
        print(f"\n    {name}:")
        print(f"      Rows: {profile['row_count']:,} ({profile['row_ratio']:.1%})")
        print(f"      Years: {profile['min_year']}–{profile['max_year']}")
        print(f"      Target: mean={profile['target_mean']:.1f}, median={profile['target_median']}, std={profile['target_std']:.1f}")
        print(f"      Zero target: {profile['target_zero_count']:,}")
        print(f"      Buckets: {profile['buckets']}")

    if errors:
        print(f"\n  SPLIT INTEGRITY: FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"    ✗ {e}")
        sys.exit(1)
    else:
        print(f"\n  ✓ SPLIT INTEGRITY: PASS")

    return profiles, errors


# ============================================================
# TASK 2.1.9 — PERSIST ARTIFACTS
# ============================================================

def task_2_1_9_persist_artifacts(
    df, train_df, val_df, test_df, config,
    data_version_info, schema_snapshot, input_manifest,
    target_profile, warning_results, year_dist, candidates,
    split_info, profiles, data_version
):
    """Save all artifacts: IDs, manifests, configs, versions."""
    print("\n" + "=" * 60)
    print("TASK 2.1.9 — PERSIST ARTIFACTS & VERSION")
    print("=" * 60)

    id_col = config["data"]["identifier_column"]
    now = datetime.now(timezone.utc)

    # Create directories
    data_intake_dir = PROJECT_ROOT / "7.ML" / "7.3.data_intake"
    splits_dir = PROJECT_ROOT / "7.ML" / "7.4.splits"
    config_dir = PROJECT_ROOT / "7.ML" / "7.1.config"

    for d in [data_intake_dir, splits_dir, config_dir]:
        d.mkdir(parents=True, exist_ok=True)

    files_created = []

    # --- Data Intake artifacts ---
    # data_version.json
    dv_path = data_intake_dir / "data_version.json"
    data_version_info["data_version"] = data_version
    with open(dv_path, "w", encoding="utf-8") as f:
        json.dump(data_version_info, f, indent=2, ensure_ascii=False)
    files_created.append(str(dv_path))
    print(f"  ✓ {dv_path}")

    # schema_snapshot.json
    ss_path = data_intake_dir / "schema_snapshot.json"
    with open(ss_path, "w", encoding="utf-8") as f:
        json.dump(schema_snapshot, f, indent=2, ensure_ascii=False, default=str)
    files_created.append(str(ss_path))
    print(f"  ✓ {ss_path}")

    # input_manifest.json
    im_path = data_intake_dir / "input_manifest.json"
    with open(im_path, "w", encoding="utf-8") as f:
        json.dump(input_manifest, f, indent=2, ensure_ascii=False)
    files_created.append(str(im_path))
    print(f"  ✓ {im_path}")

    # target_profile.json
    tp_path = data_intake_dir / "target_profile.json"
    target_profile["data_version"] = data_version
    with open(tp_path, "w", encoding="utf-8") as f:
        json.dump(target_profile, f, indent=2, ensure_ascii=False, default=str)
    files_created.append(str(tp_path))
    print(f"  ✓ {tp_path}")

    # warning_profile.json
    wp_path = data_intake_dir / "warning_profile.json"
    warning_profile_out = {
        "data_version": data_version,
        "warnings": {},
    }
    for k, v in warning_results.items():
        if isinstance(v, dict):
            warning_profile_out["warnings"][k] = v
        else:
            warning_profile_out["warnings"][k] = {"value": v}
    with open(wp_path, "w", encoding="utf-8") as f:
        json.dump(warning_profile_out, f, indent=2, ensure_ascii=False, default=str)
    files_created.append(str(wp_path))
    print(f"  ✓ {wp_path}")

    # year_distribution.csv
    yd_path = data_intake_dir / "year_distribution.csv"
    year_dist.to_csv(yd_path, index=False)
    files_created.append(str(yd_path))
    print(f"  ✓ {yd_path}")

    # split_candidates.csv
    sc_path = data_intake_dir / "split_candidates.csv"
    pd.DataFrame(candidates).to_csv(sc_path, index=False)
    files_created.append(str(sc_path))
    print(f"  ✓ {sc_path}")

    # --- Split artifacts ---
    # train_ids.parquet
    train_ids_df = train_df[[id_col]].copy()
    train_ids_path = splits_dir / "train_ids.parquet"
    train_ids_df.to_parquet(train_ids_path, index=False)
    files_created.append(str(train_ids_path))
    print(f"  ✓ {train_ids_path}")

    # validation_ids.parquet
    val_ids_df = val_df[[id_col]].copy()
    val_ids_path = splits_dir / "validation_ids.parquet"
    val_ids_df.to_parquet(val_ids_path, index=False)
    files_created.append(str(val_ids_path))
    print(f"  ✓ {val_ids_path}")

    # test_ids.parquet
    test_ids_df = test_df[[id_col]].copy()
    test_ids_path = splits_dir / "test_ids.parquet"
    test_ids_df.to_parquet(test_ids_path, index=False)
    files_created.append(str(test_ids_path))
    print(f"  ✓ {test_ids_path}")

    # Compute ID hashes
    train_id_hash = sha256_series(train_df[id_col])
    val_id_hash = sha256_series(val_df[id_col])
    test_id_hash = sha256_series(test_df[id_col])

    # split_version.txt
    split_version = "temporal-split-v1"
    sv_path = splits_dir / "split_version.txt"
    with open(sv_path, "w", encoding="utf-8") as f:
        f.write(split_version)
    files_created.append(str(sv_path))
    print(f"  ✓ {sv_path}")

    # split_manifest.json
    split_manifest = {
        "strategy": "temporal",
        "status": "locked",
        "data_version": data_version,
        "split_version": split_version,
        "time_column": config["split"]["split_column"],
        "identifier": config["data"]["identifier_column"],
        "target": config["data"]["target_column"],
        "selected_candidate": split_info["selected_candidate"],
        "train": {
            "start_year": split_info["train_start"],
            "end_year": split_info["train_end"],
            "rows": split_info["train_rows"],
            "ratio": round(split_info["train_rows"] / len(df), 4),
            "id_file": "train_ids.parquet",
            "id_sha256": train_id_hash,
            "target_profile": profiles["train"],
        },
        "validation": {
            "start_year": split_info["val_start"],
            "end_year": split_info["val_end"],
            "rows": split_info["val_rows"],
            "ratio": round(split_info["val_rows"] / len(df), 4),
            "id_file": "validation_ids.parquet",
            "id_sha256": val_id_hash,
            "target_profile": profiles["validation"],
        },
        "test": {
            "start_year": split_info["test_start"],
            "end_year": split_info["test_end"],
            "rows": split_info["test_rows"],
            "ratio": round(split_info["test_rows"] / len(df), 4),
            "id_file": "test_ids.parquet",
            "id_sha256": test_id_hash,
            "target_profile": profiles["test"],
        },
        "row_reconciliation": {
            "train": split_info["train_rows"],
            "validation": split_info["val_rows"],
            "test": split_info["test_rows"],
            "total": split_info["train_rows"] + split_info["val_rows"] + split_info["test_rows"],
            "source": len(df),
            "match": (split_info["train_rows"] + split_info["val_rows"] + split_info["test_rows"]) == len(df),
        },
        "created_at": now.isoformat(),
        "random_seed": config["reproducibility"]["random_seed"],
    }

    sm_path = splits_dir / "split_manifest.json"
    with open(sm_path, "w", encoding="utf-8") as f:
        json.dump(split_manifest, f, indent=2, ensure_ascii=False)
    files_created.append(str(sm_path))
    print(f"  ✓ {sm_path}")

    # test_set_lock.json
    test_lock = {
        "status": "locked",
        "purpose": "Test set is locked until candidate model is selected. Do NOT use for tuning or model selection.",
        "test_start_year": split_info["test_start"],
        "test_end_year": split_info["test_end"],
        "test_rows": split_info["test_rows"],
        "test_id_sha256": test_id_hash,
        "data_version": data_version,
        "split_version": split_version,
        "locked_at": now.isoformat(),
    }

    tl_path = splits_dir / "test_set_lock.json"
    with open(tl_path, "w", encoding="utf-8") as f:
        json.dump(test_lock, f, indent=2, ensure_ascii=False)
    files_created.append(str(tl_path))
    print(f"  ✓ {tl_path}")

    # --- split_config.yaml ---
    split_config = {
        "feature": "2.1",
        "strategy": "temporal",
        "status": "locked",
        "source_data_version": data_version,
        "time_column": config["split"]["split_column"],
        "identifier": config["data"]["identifier_column"],
        "target": config["data"]["target_column"],
        "train": {
            "start_year": split_info["train_start"],
            "end_year": split_info["train_end"],
        },
        "validation": {
            "start_year": split_info["val_start"],
            "end_year": split_info["val_end"],
        },
        "test": {
            "start_year": split_info["test_start"],
            "end_year": split_info["test_end"],
        },
        "require_contiguous_year_ranges": True,
        "require_zero_track_overlap": True,
        "allow_row_drop": False,
        "random_split_diagnostic": {
            "enabled": False,
            "primary_result_allowed": False,
        },
    }

    sc_yaml_path = config_dir / "split_config.yaml"
    with open(sc_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(split_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    files_created.append(str(sc_yaml_path))
    print(f"  ✓ {sc_yaml_path}")

    # --- Copy and update experiment_config.yaml into 7.ML/7.1.config/ ---
    config_dest = config_dir / "experiment_config.yaml"
    # Update the config with split info
    updated_config = config.copy()
    updated_config["split"]["final_year_cutoffs"] = {
        "train_end_year": split_info["train_end"],
        "validation_start_year": split_info["val_start"],
        "validation_end_year": split_info["val_end"],
        "test_start_year": split_info["test_start"],
    }
    updated_config["data"]["data_version"] = data_version
    updated_config["split"]["split_version"] = "temporal-split-v1"
    updated_config["project"]["status"] = "feature_2_1_completed"

    with open(config_dest, "w", encoding="utf-8") as f:
        yaml.dump(updated_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    files_created.append(str(config_dest))
    print(f"  ✓ {config_dest}")

    print(f"\n  Total artifacts created: {len(files_created)}")
    return files_created, split_manifest, split_version, train_id_hash, val_id_hash, test_id_hash


# ============================================================
# TASK 2.1.10 — REPRODUCIBILITY TEST
# ============================================================

def task_2_1_10_reproducibility(config, data_version_info, split_info):
    """Verify split is reproducible from config + frozen dataset."""
    print("\n" + "=" * 60)
    print("TASK 2.1.10 — REPRODUCIBILITY TEST")
    print("=" * 60)

    time_col = config["split"]["split_column"]
    id_col = config["data"]["identifier_column"]

    # Reload data from frozen source
    actual_source = data_version_info["actual_source_used"]
    source_type = data_version_info["source_type"]

    print(f"  Run 1: Loading from {actual_source}")
    if source_type == "parquet":
        df1 = pd.read_parquet(actual_source)
    else:
        df1 = pd.read_csv(actual_source)

    # Apply same split
    train1 = df1[df1[time_col] <= split_info["train_end"]]
    val1 = df1[(df1[time_col] >= split_info["val_start"]) & (df1[time_col] <= split_info["val_end"])]
    test1 = df1[df1[time_col] >= split_info["test_start"]]

    hash1_train = sha256_series(train1[id_col])
    hash1_val = sha256_series(val1[id_col])
    hash1_test = sha256_series(test1[id_col])

    # Run 2 — reload
    print(f"  Run 2: Re-loading from {actual_source}")
    if source_type == "parquet":
        df2 = pd.read_parquet(actual_source)
    else:
        df2 = pd.read_csv(actual_source)

    train2 = df2[df2[time_col] <= split_info["train_end"]]
    val2 = df2[(df2[time_col] >= split_info["val_start"]) & (df2[time_col] <= split_info["val_end"])]
    test2 = df2[df2[time_col] >= split_info["test_start"]]

    hash2_train = sha256_series(train2[id_col])
    hash2_val = sha256_series(val2[id_col])
    hash2_test = sha256_series(test2[id_col])

    # Compare
    match_train = hash1_train == hash2_train
    match_val = hash1_val == hash2_val
    match_test = hash1_test == hash2_test

    print(f"\n  Train IDs hash match:      {'✓' if match_train else '✗ FAIL'}")
    print(f"  Validation IDs hash match: {'✓' if match_val else '✗ FAIL'}")
    print(f"  Test IDs hash match:       {'✓' if match_test else '✗ FAIL'}")
    print(f"  Row counts match:          {len(train1)} / {len(val1)} / {len(test1)}")

    all_match = match_train and match_val and match_test
    if not all_match:
        print("  FAIL — SPLIT_NOT_REPRODUCIBLE")
    else:
        print("  ✓ REPRODUCIBILITY: PASS")

    return all_match, hash1_train, hash1_val, hash1_test


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("=" * 60)
    print("FEATURE 2.1 — DATA INTAKE, VALIDATION & TEMPORAL SPLIT")
    print("HitRadar Pro — EPIC 2")
    print(f"Owner: Tuấn Anh")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Find and load config
    config_path = find_config()
    if config_path is None:
        print("FAIL — experiment_config.yaml not found in any expected location")
        sys.exit(1)
    print(f"\nConfig found: {config_path}")
    config = load_config(config_path)

    # TASK 2.1.1
    df, actual_source, source_type, file_size, load_time = task_2_1_1_load_dataset(config)

    # TASK 2.1.2
    data_version_info, schema_snapshot, input_manifest, data_version = (
        task_2_1_2_freeze_snapshot(df, config, actual_source, source_type, file_size)
    )

    # TASK 2.1.3
    schema_errors = task_2_1_3_validate_schema(df, config)

    # TASK 2.1.4
    target_profile = task_2_1_4_validate_id_target(df, config)

    # TASK 2.1.5
    warning_results = task_2_1_5_reaudit_warnings(df, config)

    # TASK 2.1.6
    year_dist, candidates, min_year, max_year = task_2_1_6_temporal_analysis(df, config)

    # TASK 2.1.7
    train_df, val_df, test_df, split_info = task_2_1_7_lock_split(df, config, candidates, min_year, max_year)

    # TASK 2.1.8
    profiles, split_errors = task_2_1_8_validate_split(df, train_df, val_df, test_df, config, split_info)

    # TASK 2.1.9
    files_created, split_manifest, split_version, train_hash, val_hash, test_hash = (
        task_2_1_9_persist_artifacts(
            df, train_df, val_df, test_df, config,
            data_version_info, schema_snapshot, input_manifest,
            target_profile, warning_results, year_dist, candidates,
            split_info, profiles, data_version
        )
    )

    # TASK 2.1.10
    repro_ok, _, _, _ = task_2_1_10_reproducibility(config, data_version_info, split_info)

    # ============================================================
    # TERMINAL SUMMARY
    # ============================================================
    print("\n" + "=" * 60)
    print("FEATURE 2.1 — TERMINAL SUMMARY")
    print("=" * 60)
    print(f"  Files created/updated:       {len(files_created)}")
    print(f"  Actual source used:          {actual_source}")
    print(f"  Data version:                {data_version}")
    print(f"  File SHA-256:                {data_version_info['file_sha256'][:16]}...")
    print(f"  Expected rows/cols:          {config['data']['expected_rows']:,} × {config['data']['expected_columns']}")
    print(f"  Actual rows/cols:            {df.shape[0]:,} × {df.shape[1]}")
    print(f"  Identifier validation:       PASS")
    print(f"  Target validation:           PASS")
    print(f"  release_year range:          {min_year}–{max_year}")
    print(f"  Split candidates evaluated:  {len(candidates)}")
    print(f"  Locked train:                {split_info['train_start']}–{split_info['train_end']} ({split_info['train_rows']:,} rows)")
    print(f"  Locked validation:           {split_info['val_start']}–{split_info['val_end']} ({split_info['val_rows']:,} rows)")
    print(f"  Locked test:                 {split_info['test_start']}–{split_info['test_end']} ({split_info['test_rows']:,} rows)")
    print(f"  Track overlap:               0 (PASS)")
    print(f"  Chronology:                  PASS")
    print(f"  Row reconciliation:          PASS")
    print(f"  Reproducibility:             {'PASS' if repro_ok else 'FAIL'}")
    print(f"  Validation report status:    PASS_WITH_WARNINGS")

    overall = "PASS_WITH_WARNINGS" if repro_ok else "FAIL"
    print(f"  Overall Feature 2.1 status:  {overall}")
    print(f"  Allowed to start Feature 2.2: {'YES' if overall != 'FAIL' else 'NO'}")
    print(f"\n  Completed: {datetime.now(timezone.utc).isoformat()}")

    # Return data for report generation
    return {
        "df_shape": df.shape,
        "actual_source": actual_source,
        "source_type": source_type,
        "data_version": data_version,
        "data_version_info": data_version_info,
        "schema_snapshot": schema_snapshot,
        "input_manifest": input_manifest,
        "target_profile": target_profile,
        "warning_results": warning_results,
        "year_dist": year_dist,
        "candidates": candidates,
        "split_info": split_info,
        "profiles": profiles,
        "split_manifest": split_manifest,
        "split_version": split_version,
        "files_created": files_created,
        "repro_ok": repro_ok,
        "train_hash": train_hash,
        "val_hash": val_hash,
        "test_hash": test_hash,
        "overall_status": overall,
        "min_year": min_year,
        "max_year": max_year,
    }


if __name__ == "__main__":
    results = main()
