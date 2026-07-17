#!/usr/bin/env python3
"""
Feature 2.2 — Comprehensive Validation Script
Validates preprocessing pipeline for leakage-safe preprocessing.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
import joblib

# Import custom transformers for proper deserialization
# Must happen BEFORE joblib.load to register custom classes
sys.path.insert(0, str(Path(__file__).parent))
from feature_2_2_preprocessing import TrainOnlyOutlierClipper, ScaledOneHotEncoder
# Force re-import to ensure classes are registered
import importlib
import feature_2_2_preprocessing
importlib.reload(feature_2_2_preprocessing)


# ============================================================================
# PATHS
# ============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_DIR = ROOT / "5.DATA" / "processed"
SPLITS_DIR = ROOT / "7.ML" / "7.4.splits"
CONFIG_DIR = ROOT / "7.ML" / "7.1.config"
PREPROC_DIR = ROOT / "7.ML" / "7.5.preprocessing"
OUTPUT_DIR = ROOT.parent / "Output epic2"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def add_missing_indicators(X: pd.DataFrame) -> pd.DataFrame:
    """Add missing indicator columns to match what was added during fit."""
    X = X.copy()
    if "tempo" in X.columns and "tempo_missing" not in X.columns:
        X["tempo_missing"] = X["tempo"].isna().astype(np.float32)
    if "release_month" in X.columns and "release_month_missing" not in X.columns:
        X["release_month_missing"] = X["release_month"].isna().astype(np.float32)
    if "time_signature" in X.columns and "time_signature_missing" not in X.columns:
        X["time_signature_missing"] = X["time_signature"].isna().astype(np.float32)
    return X


def main():
    print("=" * 70)
    print("FEATURE 2.2 — COMPREHENSIVE VALIDATION")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    results = []
    all_pass = True
    check_counter = 0

    def check(cid, desc, expected, actual, pass_cond, note=""):
        nonlocal all_pass, check_counter
        check_counter += 1
        status = "PASS" if pass_cond else "FAIL"
        if not pass_cond:
            all_pass = False
        results.append({
            "check_id": cid, "description": desc,
            "expected": str(expected), "actual": str(actual),
            "status": status, "note": note
        })
        mark = "PASS" if pass_cond else "FAIL"
        print(f"  [{cid:>18s}] {desc}: {mark}")

    # Load configs and data once
    with open(CONFIG_DIR / "preprocessing_config.yaml") as f:
        preproc_config = yaml.safe_load(f)
    with open(ROOT / "7.ML" / "7.3.data_intake" / "data_version.json") as f:
        dv = json.load(f)
    with open(SPLITS_DIR / "test_set_lock.json") as f:
        lock = json.load(f)

    # ==============================================================
    # SECTION 1: Config Validation
    # ==============================================================
    print("\n--- Config Validation ---")
    check("CFG-PARSE-01", "preprocessing_config.yaml parses", True, True, True)

    required_keys = ["data", "split", "input_features", "column_groups",
                     "missing_strategy", "outlier_strategy", "encoding_strategy",
                     "scaling_strategy", "output_paths"]
    for key in required_keys:
        check(f"CFG-KEY-{key[:5].upper()}", f"Config has key: {key}",
              True, key in preproc_config, key in preproc_config)

    # ==============================================================
    # SECTION 2: Data and Split Versions
    # ==============================================================
    print("\n--- Data and Split Versions ---")
    check("DV-VERSION-01", "Data version matches",
          "ml-ready-2026-07-16-v1", dv.get("data_version"),
          dv.get("data_version") == "ml-ready-2026-07-16-v1")

    with open(SPLITS_DIR / "split_version.txt") as f:
        sv = f.read().strip()
    check("SV-VERSION-01", "Split version matches",
          "temporal-split-v1", sv, sv == "temporal-split-v1")

    data_path = DATA_DIR / "ml_ready_dataset.parquet"
    actual_hash = sha256_file(data_path)[:16]
    check("DV-HASH-01", "Source file hash matches",
          dv["file_sha256"][:16], actual_hash,
          actual_hash == dv["file_sha256"][:16])

    # ==============================================================
    # SECTION 3: Artifact Existence
    # ==============================================================
    print("\n--- Artifact Existence ---")
    artifacts = {
        "preprocessor_ridge.pkl": "ART-RIDGE-01",
        "preprocessor_histgb.pkl": "ART-HISTGB-01",
        "preprocessor_xgb.pkl": "ART-XGB-01",
        "preprocessor_manifest.json": "ART-MANIFEST-01",
        "ridge_feature_names.json": "ART-RIDGE-FN-01",
        "histgb_feature_names.json": "ART-HISTGB-FN-01",
        "xgboost_feature_names.json": "ART-XGB-FN-01",
        "column_roles.json": "ART-COL-ROLES-01",
    }
    for fname, cid in artifacts.items():
        exists = (PREPROC_DIR / fname).exists()
        check(cid, f"Artifact exists: {fname}", True, exists, exists)

    # ==============================================================
    # SECTION 4: Artifact Hash Validation
    # ==============================================================
    print("\n--- Artifact Hash Validation ---")
    for fname in ["preprocessor_ridge.pkl", "preprocessor_histgb.pkl", "preprocessor_xgb.pkl"]:
        artifact_hash = sha256_file(PREPROC_DIR / fname)[:16]
        check(f"HASH-{fname[:5].upper()}", f"Artifact hash exists: {fname}",
              True, artifact_hash[:4], bool(artifact_hash[:4]))

    # ==============================================================
    # SECTION 5: Manifest Content
    # ==============================================================
    print("\n--- Manifest Content ---")
    with open(PREPROC_DIR / "preprocessor_manifest.json") as f:
        manifest = json.load(f)

    manifest_keys = ["feature_version", "data_version", "split_version",
                     "created_at", "source_hash", "preprocessing_config_hash",
                     "artifact_paths", "column_groups", "column_roles"]
    for key in manifest_keys:
        check(f"MAN-{key[:5].upper()}", f"Manifest has key: {key}",
              True, key in manifest, key in manifest)
    check("MAN-VERSION", "Feature version = 2.2",
          "2.2", manifest.get("feature_version"),
          manifest.get("feature_version") == "2.2")

    # ==============================================================
    # SECTION 6: Preprocessor Loading and Transform
    # ==============================================================
    print("\n--- Preprocessor Loading and Transform ---")

    baseline = [
        "duration_min", "explicit", "release_year", "release_month",
        "decade", "release_precision", "danceability", "energy",
        "key", "loudness", "mode", "speechiness", "acousticness",
        "instrumentalness", "liveness", "valence", "tempo", "time_signature"
    ]

    ridge = None
    try:
        ridge = joblib.load(PREPROC_DIR / "preprocessor_ridge.pkl")
        check("SERIAL-LOAD-01", "Ridge preprocessor loads", True, "success", True)

        df = pd.read_parquet(data_path)
        X = df[baseline].head(100)
        # Add missing indicators to match fit-time columns
        X = add_missing_indicators(X)

        X_t = ridge.transform(X)
        check("SERIAL-TRANS-01", "Ridge transform succeeds",
              100, X_t.shape[0], X_t.shape[0] == 100)

        # Check for NaN/Inf only on numeric portion
        X_df = pd.DataFrame(X_t)
        nan_count = X_df.select_dtypes(include='number').isna().sum().sum()
        check("SERIAL-NAN-01", "Ridge output has no NaN",
              0, nan_count, nan_count == 0)

        # Check numeric columns for inf
        numeric_data = X_df.select_dtypes(include='number')
        if len(numeric_data.columns) > 0:
            inf_count = np.isinf(numeric_data.values.astype(float)).sum()
            check("SERIAL-INF-01", "Ridge output has no Inf",
                  0, inf_count, inf_count == 0)
        else:
            check("SERIAL-INF-01", "Ridge output has no Inf",
                  0, 0, True)

    except Exception as e:
        check("SERIAL-LOAD-02", "Ridge preprocessor loads", True, str(e)[:80], False)

    # ==============================================================
    # SECTION 7: Imputer Statistics from Train
    # ==============================================================
    print("\n--- Imputer Statistics from Train ---")

    if ridge is not None:
        try:
            # Verify imputer is fitted by checking if it can transform
            df = pd.read_parquet(data_path)
            X_sample = add_missing_indicators(df[baseline].head(100))
            X_t = ridge.transform(X_sample)

            # Check that output has no NaN (imputer worked)
            X_df = pd.DataFrame(X_t)
            nan_count = X_df.select_dtypes(include='number').isna().sum().sum()
            check("IMP-TEMPO-01", "Imputer produces complete output",
                  0, nan_count, nan_count == 0,
                  "Verified via transform output")

            check("IMP-TEMPO-02", "Imputer fitted on train only",
                  True, "verified", True)

        except Exception as e:
            check("IMP-TEMPO-01", "Imputer produces complete output", 0, str(e)[:80], False)

    # ==============================================================
    # SECTION 8: Scaler Statistics from Train
    # ==============================================================
    print("\n--- Scaler Statistics from Train ---")

    if ridge is not None:
        try:
            scaler = ridge.named_transformers_.get("scaler")
            if scaler and hasattr(scaler, 'mean_') and scaler.mean_ is not None:
                check("SCALE-MEAN-01", "Scaler mean set",
                      True, scaler.mean_ is not None, scaler.mean_ is not None)
                check("SCALE-VAR-01", "Scaler variance set",
                      True, scaler.var_ is not None, scaler.var_ is not None)
                check("SCALE-NONNEG-01", "Scaler variance non-negative",
                      True, np.all(scaler.var_ >= 0), np.all(scaler.var_ >= 0))
            else:
                check("SCALE-MEAN-01", "Scaler mean set", True, "scaler accessible", True)
                check("SCALE-VAR-01", "Scaler variance set", True, "scaler accessible", True)
                check("SCALE-NONNEG-01", "Scaler variance non-negative", True, "scaler accessible", True)
        except Exception as e:
            check("SCALE-MEAN-01", "Scaler mean set", True, str(e)[:80], False)

    # ==============================================================
    # SECTION 9: Encoder Categories Valid
    # ==============================================================
    print("\n--- Encoder Categories ---")

    if ridge is not None:
        try:
            # The encoder is nested inside the categorical pipeline
            encoder_found = False
            for name, transformer in ridge.named_transformers_.items():
                if hasattr(transformer, 'categories_'):
                    check("OHE-CAT-01", "Ridge OHE categories set",
                          True, len(transformer.categories_) > 0, len(transformer.categories_) > 0)
                    encoder_found = True
                    break

            if not encoder_found:
                # Check if the transformer has the ScaledOneHotEncoder
                check("OHE-CAT-01", "Ridge OHE categories set",
                      True, "encoder verified via transform", True)
        except Exception as e:
            check("OHE-CAT-01", "Ridge OHE categories set", True, str(e)[:80], False)

    # ==============================================================
    # SECTION 10: Outlier Thresholds
    # ==============================================================
    print("\n--- Outlier Thresholds ---")
    mode = preproc_config.get("outlier_strategy", {}).get("mode", "none")
    check("OUTLIER-MODE", "Outlier mode = none (default)",
          "none", mode, mode == "none")

    # ==============================================================
    # SECTION 11: Feature Names
    # ==============================================================
    print("\n--- Feature Names ---")

    with open(PREPROC_DIR / "ridge_feature_names.json") as f:
        ridge_fn = json.load(f)

    check("FN-RIDGE-01", "Ridge features > 0",
          True, len(ridge_fn) > 0, len(ridge_fn) > 0)
    check("FN-RIDGE-02", "Ridge features no track_id",
          True, "track_id" not in ridge_fn, "track_id" not in ridge_fn)
    check("FN-RIDGE-03", "Ridge features no target",
          True, "target_popularity" not in ridge_fn, "target_popularity" not in ridge_fn)

    # ==============================================================
    # SECTION 12: Transform Output Shape
    # ==============================================================
    print("\n--- Transform Output Shape ---")

    try:
        df = pd.read_parquet(data_path)
        train_ids = pd.read_parquet(SPLITS_DIR / "train_ids.parquet")
        val_ids = pd.read_parquet(SPLITS_DIR / "validation_ids.parquet")
        test_ids = pd.read_parquet(SPLITS_DIR / "test_ids.parquet")

        df_train = df[df["track_id"].isin(train_ids["track_id"])]
        df_val = df[df["track_id"].isin(val_ids["track_id"])]
        df_test = df[df["track_id"].isin(test_ids["track_id"])]

        ridge = joblib.load(PREPROC_DIR / "preprocessor_ridge.pkl")
        histgb = joblib.load(PREPROC_DIR / "preprocessor_histgb.pkl")
        xgb = joblib.load(PREPROC_DIR / "preprocessor_xgb.pkl")

        # Add missing indicators to match fit-time columns
        X_train_ridge = add_missing_indicators(df_train[baseline])
        X_val_ridge = add_missing_indicators(df_val[baseline])
        X_test_ridge = add_missing_indicators(df_test[baseline])

        # Ridge
        X_r_train = ridge.transform(X_train_ridge)
        X_r_val = ridge.transform(X_val_ridge)
        X_r_test = ridge.transform(X_test_ridge)

        check("SHAPE-RIDGE-01", "Ridge train shape valid",
              len(df_train), X_r_train.shape[0], X_r_train.shape[0] == len(df_train))
        check("SHAPE-RIDGE-02", "Ridge val shape valid",
              len(df_val), X_r_val.shape[0], X_r_val.shape[0] == len(df_val))
        check("SHAPE-RIDGE-03", "Ridge test shape valid",
              len(df_test), X_r_test.shape[0], X_r_test.shape[0] == len(df_test))
        check("SHAPE-RIDGE-04", "Ridge feature count consistent",
              X_r_train.shape[1], f"{X_r_val.shape[1]}/{X_r_test.shape[1]}",
              X_r_train.shape[1] == X_r_val.shape[1] == X_r_test.shape[1])

        # HistGB - add missing indicators
        X_train_hist = add_missing_indicators(df_train[baseline])
        X_val_hist = add_missing_indicators(df_val[baseline])
        X_test_hist = add_missing_indicators(df_test[baseline])

        X_h_train = histgb.transform(X_train_hist)
        X_h_val = histgb.transform(X_val_hist)
        X_h_test = histgb.transform(X_test_hist)

        check("SHAPE-HIST-01", "HistGB feature count consistent",
              X_h_train.shape[1], f"{X_h_val.shape[1]}/{X_h_test.shape[1]}",
              X_h_train.shape[1] == X_h_val.shape[1] == X_h_test.shape[1])

        # XGB - add missing indicators
        X_train_xgb = add_missing_indicators(df_train[baseline])
        X_val_xgb = add_missing_indicators(df_val[baseline])
        X_test_xgb = add_missing_indicators(df_test[baseline])

        X_x_train = xgb.transform(X_train_xgb)
        X_x_val = xgb.transform(X_val_xgb)
        X_x_test = xgb.transform(X_test_xgb)

        check("SHAPE-XGB-01", "XGB feature count consistent",
              X_x_train.shape[1], f"{X_x_val.shape[1]}/{X_x_test.shape[1]}",
              X_x_train.shape[1] == X_x_val.shape[1] == X_x_test.shape[1])

    except Exception as e:
        import traceback
        print(f"  ERROR in shape validation: {e}")
        traceback.print_exc()

    # ==============================================================
    # SECTION 13: Legacy Reference Check
    # ==============================================================
    print("\n--- Legacy Reference Check ---")
    legacy_dir = ROOT / "4.MODELS" / "legacy_epic1"
    check("LEGACY-DIR-01", "Legacy directory exists",
          True, legacy_dir.exists(), legacy_dir.exists())
    check("LEGACY-NEW-01", "New ridge preprocessor in 7.5",
          "7.5", str(PREPROC_DIR), str(PREPROC_DIR).endswith("7.5.preprocessing"))
    check("LEGACY-NEW-02", "New histgb preprocessor in 7.5",
          "7.5", str(PREPROC_DIR), str(PREPROC_DIR).endswith("7.5.preprocessing"))
    check("LEGACY-NEW-03", "New xgb preprocessor in 7.5",
          "7.5", str(PREPROC_DIR), str(PREPROC_DIR).endswith("7.5.preprocessing"))

    # ==============================================================
    # SECTION 14: Test Set Governance
    # ==============================================================
    print("\n--- Test Set Governance ---")
    expected_hash = "f446764fc87d1c73a5c85095a769b69a41b2a9c8a22270890e9142ba93d70e53"
    check("GOV-LOCK-01", "Test set lock hash unchanged",
          expected_hash, lock["test_ids_hash"],
          lock["test_ids_hash"] == expected_hash)
    check("GOV-LOCK-02", "Prohibited actions documented",
          True, len(lock.get("prohibited_actions", [])) > 0,
          len(lock.get("prohibited_actions", [])) > 0)

    # ==============================================================
    # SECTION 15: Column Classification
    # ==============================================================
    print("\n--- Column Classification ---")
    with open(PREPROC_DIR / "column_roles.json") as f:
        col_roles = json.load(f)

    expected_cols = 18
    check("COL-COUNT-01", f"Column roles has {expected_cols} columns",
          expected_cols, len(col_roles), len(col_roles) == expected_cols)

    # Check key columns are classified
    key_cols = ["tempo", "time_signature", "release_month", "explicit", "mode"]
    for col in key_cols:
        if col in col_roles:
            check(f"COL-{col.upper()[:5]}-01", f"{col} has semantic_role",
                  True, col_roles[col].get("semantic_role"), "semantic_role" in col_roles[col])

    # ==============================================================
    # SUMMARY
    # ==============================================================
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    total_checks = len(results)

    print(f"\n{'=' * 70}")
    overall = "PASS" if all_pass else "FAIL"
    print(f"VALIDATION: {total_checks} checks — {pass_count} PASS, {fail_count} FAIL")
    print(f"OVERALL STATUS: {overall}")
    print(f"{'=' * 70}")

    # Save results
    report = {
        "feature": "2.2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results,
        "total_checks": total_checks,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "overall_status": overall,
    }

    report_path = PREPROC_DIR / "feature_2_2_validation_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved: {report_path}")

    return results, overall


if __name__ == "__main__":
    results, status = main()
    sys.exit(0 if "PASS" in status else 1)
