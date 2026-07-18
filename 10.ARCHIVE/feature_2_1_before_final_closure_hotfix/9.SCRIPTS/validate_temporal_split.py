#!/usr/bin/env python3
"""
Task 2.1.8 / 2.1.11 — Validate Temporal Split
HitRadar Pro — EPIC 2, Feature 2.1

Standalone validation script. Does NOT train models or fit preprocessors.
"""

import sys
import json
import hashlib
from pathlib import Path

import yaml
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def sha256_series(series):
    h = hashlib.sha256()
    for val in series.sort_values().values:
        h.update(str(val).encode("utf-8"))
    return h.hexdigest()


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main(config_path=None):
    print("=" * 60)
    print("VALIDATE TEMPORAL SPLIT — Feature 2.1")
    print("=" * 60)

    # Load configs
    if config_path is None:
        config_path = PROJECT_ROOT / "7.ML" / "7.1.config" / "split_config.yaml"
    split_config = load_config(config_path)

    exp_config_path = PROJECT_ROOT / "7.ML" / "7.1.config" / "experiment_config.yaml"
    exp_config = load_config(exp_config_path)

    # Load manifest
    manifest_path = PROJECT_ROOT / "7.ML" / "7.4.splits" / "split_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Load data version
    dv_path = PROJECT_ROOT / "7.ML" / "7.3.data_intake" / "data_version.json"
    with open(dv_path, "r", encoding="utf-8") as f:
        data_version = json.load(f)

    # Load source dataset
    source = data_version["actual_source_used"]
    if source.endswith(".parquet"):
        df = pd.read_parquet(source)
    else:
        df = pd.read_csv(source)

    time_col = split_config["time_column"]
    id_col = split_config["identifier"]
    tgt_col = split_config["target"]

    results = []
    all_pass = True

    def check(check_id, desc, expected, actual, pass_cond):
        nonlocal all_pass
        status = "PASS" if pass_cond else "FAIL"
        if not pass_cond:
            all_pass = False
        results.append({
            "check_id": check_id, "description": desc,
            "expected": str(expected), "actual": str(actual), "status": status
        })
        mark = "✓" if pass_cond else "✗"
        print(f"  {mark} [{check_id}] {desc}: expected={expected}, actual={actual} → {status}")

    # 1. Split config parsed
    check("SC-01", "split_config.yaml parsed", True, True, True)
    check("SC-02", "Strategy is temporal", "temporal", split_config["strategy"],
          split_config["strategy"] == "temporal")
    check("SC-03", "Status is locked", "locked", split_config["status"],
          split_config["status"] == "locked")

    # 2. Year boundaries not null
    train_end = split_config["train"]["end_year"]
    val_start = split_config["validation"]["start_year"]
    val_end = split_config["validation"]["end_year"]
    test_start = split_config["test"]["start_year"]

    check("SC-04", "train.end_year not null", "not null", train_end, train_end is not None)
    check("SC-05", "validation.start_year not null", "not null", val_start, val_start is not None)
    check("SC-06", "test.start_year not null", "not null", test_start, test_start is not None)

    # 3. Apply split
    train_df = df[df[time_col] <= train_end]
    val_df = df[(df[time_col] >= val_start) & (df[time_col] <= val_end)]
    test_df = df[df[time_col] >= test_start]

    # 4. Overlap checks
    train_ids = set(train_df[id_col])
    val_ids = set(val_df[id_col])
    test_ids = set(test_df[id_col])

    tv = len(train_ids & val_ids)
    tt = len(train_ids & test_ids)
    vt = len(val_ids & test_ids)

    check("OV-01", "train ∩ validation overlap", 0, tv, tv == 0)
    check("OV-02", "train ∩ test overlap", 0, tt, tt == 0)
    check("OV-03", "validation ∩ test overlap", 0, vt, vt == 0)

    # 5. Duplicate/NULL within splits
    for name, sdf in [("train", train_df), ("val", val_df), ("test", test_df)]:
        dup = int(sdf[id_col].duplicated().sum())
        null = int(sdf[id_col].isnull().sum())
        check(f"DUP-{name}", f"{name} duplicate track_id", 0, dup, dup == 0)
        check(f"NULL-{name}", f"{name} NULL track_id", 0, null, null == 0)

    # 6. Row reconciliation
    total = len(train_df) + len(val_df) + len(test_df)
    check("ROW-01", "Row reconciliation", len(df), total, total == len(df))

    # 7. Chronology
    t_max = int(train_df[time_col].max())
    v_min = int(val_df[time_col].min())
    v_max = int(val_df[time_col].max())
    te_min = int(test_df[time_col].min())

    check("CHR-01", "max(train) < min(val)", f"{t_max} < {v_min}", t_max < v_min, t_max < v_min)
    check("CHR-02", "max(val) < min(test)", f"{v_max} < {te_min}", v_max < te_min, v_max < te_min)

    # 8. Test contains max year
    ds_max = int(df[time_col].max())
    test_has_max = ds_max in test_df[time_col].values
    check("CHR-03", "Test contains dataset max year", ds_max, ds_max if test_has_max else "missing", test_has_max)

    # 9. Manifest consistency
    check("MAN-01", "Manifest train rows", manifest["train"]["rows"], len(train_df),
          manifest["train"]["rows"] == len(train_df))
    check("MAN-02", "Manifest val rows", manifest["validation"]["rows"], len(val_df),
          manifest["validation"]["rows"] == len(val_df))
    check("MAN-03", "Manifest test rows", manifest["test"]["rows"], len(test_df),
          manifest["test"]["rows"] == len(test_df))

    # 10. ID hash verification
    train_hash = sha256_series(train_df[id_col])
    val_hash = sha256_series(val_df[id_col])
    test_hash = sha256_series(test_df[id_col])

    check("HASH-01", "Train ID hash match", manifest["train"]["id_sha256"][:16],
          train_hash[:16], train_hash == manifest["train"]["id_sha256"])
    check("HASH-02", "Val ID hash match", manifest["validation"]["id_sha256"][:16],
          val_hash[:16], val_hash == manifest["validation"]["id_sha256"])
    check("HASH-03", "Test ID hash match", manifest["test"]["id_sha256"][:16],
          test_hash[:16], test_hash == manifest["test"]["id_sha256"])

    # 11. Data version consistency
    check("VER-01", "Data version in manifest matches frozen",
          data_version["data_version"], manifest["data_version"],
          data_version["data_version"] == manifest["data_version"])

    # 12. No preprocessing artifacts from 2.1
    models_dir = PROJECT_ROOT / "4.MODELS" / "4.1.trained"
    pkl_files = list(models_dir.glob("*.pkl")) if models_dir.exists() else []
    check("SCOPE-01", "No new model artifacts from 2.1", 0, len(pkl_files), len(pkl_files) == 0)

    # Summary
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")

    print(f"\n{'=' * 60}")
    print(f"VALIDATION RESULT: {pass_count} PASS, {fail_count} FAIL")
    overall = "PASS" if all_pass else "FAIL"
    print(f"OVERALL: {overall}")
    print(f"{'=' * 60}")

    return results, overall


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None, help="Path to split_config.yaml")
    args = parser.parse_args()
    config_path = Path(args.config) if args.config else None
    results, status = main(config_path)
    sys.exit(0 if status == "PASS" else 1)
