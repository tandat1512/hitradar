#!/usr/bin/env python3
"""
Feature 2.1 — Comprehensive Validation Script (HOTFIX version)
HOTFIX 6: Upgraded from file-existence to content-level semantic validation.
All check IDs are unique. Content validated for all JSON/YAML artifacts.
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import yaml
import pandas as pd
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_series(series):
    h = hashlib.sha256()
    for val in sorted(series.astype(str).values):
        h.update(val.encode("utf-8"))
    return h.hexdigest()


def main():
    print("=" * 70)
    print("FEATURE 2.1 — COMPREHENSIVE VALIDATION (HOTFIX)")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    results = []
    all_pass = True

    # Commit SHA for results
    import subprocess
    try:
        commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    except:
        commit_sha = "UNKNOWN"

    def check(cid, desc, expected, actual, pass_cond, note=""):
        nonlocal all_pass
        status = "PASS" if pass_cond else "FAIL"
        severity = "ERROR" if not pass_cond else "INFO"
        if not pass_cond:
            all_pass = False
        
        # Derive category from cid (e.g. CFG-KEY-XXX -> CFG)
        category = cid.split("-")[0] if "-" in cid else "GENERAL"
            
        results.append({
            "check_id": cid, 
            "category": category,
            "description": desc,
            "expected": str(expected), 
            "actual": str(actual),
            "evidence_path": "",
            "severity": severity,
            "status": status, 
            "validator_version": "2.1.2",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository_commit_sha": commit_sha,
            "note": note
        })
        mark = "PASS" if pass_cond else "FAIL"
        print(f"  [{cid:>18s}] {desc}: {mark}")

    # ==============================================================
    # SECTION 1: Feature 2.0 prerequisites
    # ==============================================================
    print("\n--- Feature 2.0 Prerequisites ---")
    f20_dir = ROOT.parent / "Output epic2" / "F 2.0"
    f20_files = {
        "EPIC2_SCOPE_LOCK.md": "F20-PREREQ-01",
        "ML_CONTRACT.md": "F20-PREREQ-02",
        "EXPERIMENT_DESIGN.md": "F20-PREREQ-03",
        "experiment_config.yaml": "F20-PREREQ-04",
        "EPIC2_DEFINITION_OF_DONE.md": "F20-PREREQ-05",
        "FEATURE_2_0_COMPLETION_REPORT.md": "F20-PREREQ-06",
    }
    for fname, cid in f20_files.items():
        exists = (f20_dir / fname).exists()
        check(cid, f"Feature 2.0: {fname}", True, exists, exists)

    # ==============================================================
    # SECTION 2: Config content validation
    # ==============================================================
    print("\n--- Config Content Validation ---")
    config_path = ROOT / "7.ML" / "7.1.config" / "experiment_config.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        check("CFG-PARSE-01", "experiment_config.yaml parses", True, True, True)
    except Exception as e:
        check("CFG-PARSE-01", "experiment_config.yaml parses", True, str(e), False)
        print("FATAL: Cannot continue")
        return results, "FAIL"

    # Required top-level keys
    for key in ["project", "data", "split", "leakage_rules", "reproducibility"]:
        check(f"CFG-KEY-{key[:5].upper()}", f"Config has key: {key}",
              True, key in config, key in config)

    sc_path = ROOT / "7.ML" / "7.1.config" / "split_config.yaml"
    try:
        with open(sc_path, "r", encoding="utf-8") as f:
            sc = yaml.safe_load(f)
        check("CFG-PARSE-02", "split_config.yaml parses", True, True, True)
    except Exception as e:
        check("CFG-PARSE-02", "split_config.yaml parses", True, str(e), False)
        return results, "FAIL"

    check("CFG-SPLIT-01", "Split strategy = temporal", "temporal", sc["strategy"],
          sc["strategy"] == "temporal")
    check("CFG-SPLIT-02", "Split status = locked", "locked", sc["status"],
          sc["status"] == "locked")

    # ==============================================================
    # SECTION 3: Data version content validation
    # ==============================================================
    print("\n--- Data Version Content Validation ---")
    dv_path = ROOT / "7.ML" / "7.3.data_intake" / "data_version.json"
    try:
        with open(dv_path, "r", encoding="utf-8") as f:
            dv = json.load(f)
        check("DV-PARSE-01", "data_version.json parses", True, True, True)
    except Exception as e:
        check("DV-PARSE-01", "data_version.json parses", True, str(e), False)
        return results, "FAIL"

    for key in ["data_version", "actual_source_used", "rows", "columns", "file_sha256", "schema_hash"]:
        check(f"DV-KEY-{key[:6].upper()}", f"data_version has key: {key}",
              True, key in dv, key in dv)

    check("DV-ROWS-01", "data_version rows = 586672", 586672, dv.get("rows"), dv.get("rows") == 586672)
    check("DV-COLS-01", "data_version cols = 20", 20, dv.get("columns"), dv.get("columns") == 20)

    # Verify file hash
    source_path = Path(dv["actual_source_used"])
    if source_path.exists():
        actual_hash = sha256_file(source_path)
        check("DV-HASH-01", "File SHA-256 matches frozen hash",
              dv["file_sha256"][:16], actual_hash[:16],
              actual_hash == dv["file_sha256"])
    else:
        check("DV-HASH-01", "Source file exists", True, False, False)

    # ==============================================================
    # SECTION 4: Load and validate dataset
    # ==============================================================
    print("\n--- Dataset Validation ---")
    if source_path.exists():
        df = pd.read_parquet(source_path) if str(source_path).endswith(".parquet") else pd.read_csv(source_path)
    else:
        print("FATAL: Source file not found")
        return results, "FAIL"

    check("DATA-ROWS-01", "Row count = 586672", 586672, df.shape[0], df.shape[0] == 586672)
    check("DATA-COLS-01", "Column count = 20", 20, df.shape[1], df.shape[1] == 20)

    # Schema
    baseline = config["data"]["baseline_features"]
    id_col = config["data"]["identifier_column"]
    tgt_col = config["data"]["target_column"]
    expected_cols = [id_col, tgt_col] + baseline
    all_present = all(c in df.columns for c in expected_cols)
    check("DATA-SCHEMA-01", "All 20 official columns present", True, all_present, all_present)

    # Forbidden columns
    forbidden = config["data"]["forbidden_columns"]
    forbidden_found = [c for c in forbidden if c in baseline]
    check("DATA-LEAK-01", "No forbidden leakage columns in features", 0, len(forbidden_found),
          len(forbidden_found) == 0)
    check("DATA-LEAK-02", f"{tgt_col} not in features", True, tgt_col not in baseline,
          tgt_col not in baseline)
    check("DATA-LEAK-03", f"{id_col} not in features", True, id_col not in baseline,
          id_col not in baseline)

    # Identifier
    id_null = int(df[id_col].isnull().sum())
    id_dup = int(df[id_col].duplicated().sum())
    check("ID-NULL-01", f"{id_col} NULL count", 0, id_null, id_null == 0)
    check("ID-DUP-01", f"{id_col} duplicate count", 0, id_dup, id_dup == 0)

    # Target
    tgt = df[tgt_col]
    check("TGT-NULL-01", "target NULL count", 0, int(tgt.isnull().sum()), tgt.isnull().sum() == 0)
    check("TGT-NAN-01", "target NaN count", 0, int(np.isnan(tgt).sum()), np.isnan(tgt).sum() == 0)
    check("TGT-INF-01", "target infinite count", 0, int(np.isinf(tgt).sum()), np.isinf(tgt).sum() == 0)
    check("TGT-MIN-01", "target min >= 0", True, float(tgt.min()) >= 0, float(tgt.min()) >= 0)
    check("TGT-MAX-01", "target max <= 100", True, float(tgt.max()) <= 100, float(tgt.max()) <= 100)

    # release_year NULL (critical for temporal split)
    ry_null = int(df["release_year"].isnull().sum())
    check("SPLIT-RY-NULL-01", "release_year NULL count (for split)", 0, ry_null, ry_null == 0)

    # ==============================================================
    # SECTION 5: Data exceptions
    # ==============================================================
    print("\n--- Data Exceptions ---")
    exc_path = ROOT / "7.ML" / "7.3.data_intake" / "data_exceptions.json"
    if exc_path.exists():
        with open(exc_path, "r", encoding="utf-8") as f:
            exc_data = json.load(f)
        check("EXC-FILE-01", "data_exceptions.json exists and parses", True, True, True)

        # Check year 1900 is registered
        year_1900_exc = [e for e in exc_data.get("exceptions", []) if e.get("value") == 1900]
        check("EXC-YEAR1900-01", "Year 1900 anomaly registered in exceptions",
              True, len(year_1900_exc) > 0, len(year_1900_exc) > 0)
    else:
        check("EXC-FILE-01", "data_exceptions.json exists", True, False, False)

    # ==============================================================
    # SECTION 6: Schema snapshot content validation
    # ==============================================================
    print("\n--- Schema Snapshot Validation ---")
    ss_path = ROOT / "7.ML" / "7.3.data_intake" / "schema_snapshot.json"
    if ss_path.exists():
        with open(ss_path, "r", encoding="utf-8") as f:
            ss = json.load(f)
        check("SS-PARSE-01", "schema_snapshot.json parses", True, True, True)
        check("SS-COLS-01", "schema_snapshot column count",
              20, len(ss.get("columns", [])), len(ss.get("columns", [])) == 20)
        # Data version consistency
        check("SS-DV-01", "schema_snapshot data_version matches",
              dv["data_version"], ss.get("data_version"), dv["data_version"] == ss.get("data_version"))
    else:
        check("SS-PARSE-01", "schema_snapshot.json exists", True, False, False)

    # ==============================================================
    # SECTION 7: Input manifest content validation
    # ==============================================================
    print("\n--- Input Manifest Validation ---")
    im_path = ROOT / "7.ML" / "7.3.data_intake" / "input_manifest.json"
    if im_path.exists():
        with open(im_path, "r", encoding="utf-8") as f:
            im = json.load(f)
        check("IM-PARSE-01", "input_manifest.json parses", True, True, True)
        check("IM-ROWS-01", "input_manifest actual_rows matches",
              586672, im.get("actual_rows"), im.get("actual_rows") == 586672)
        check("IM-HASH-01", "input_manifest schema_hash matches data_version",
              dv.get("schema_hash", "")[:16], im.get("schema_hash", "")[:16],
              dv.get("schema_hash") == im.get("schema_hash"))
    else:
        check("IM-PARSE-01", "input_manifest.json exists", True, False, False)

    # ==============================================================
    # SECTION 8: Target profile content validation
    # ==============================================================
    print("\n--- Target Profile Validation ---")
    tp_path = ROOT / "7.ML" / "7.3.data_intake" / "target_profile.json"
    if tp_path.exists():
        with open(tp_path, "r", encoding="utf-8") as f:
            tp = json.load(f)
        check("TP-PARSE-01", "target_profile.json parses", True, True, True)
        check("TP-COUNT-01", "target_profile count", 586672, tp.get("count"), tp.get("count") == 586672)
        check("TP-NULL-01", "target_profile null_count", 0, tp.get("null_count"), tp.get("null_count") == 0)
    else:
        check("TP-PARSE-01", "target_profile.json exists", True, False, False)

    # ==============================================================
    # SECTION 9: Split artifact content validation
    # ==============================================================
    print("\n--- Split Artifact Content Validation ---")

    # Split manifest
    sm_path = ROOT / "7.ML" / "7.4.splits" / "split_manifest.json"
    if sm_path.exists():
        with open(sm_path, "r", encoding="utf-8") as f:
            sm = json.load(f)
        check("SPL-MANIFEST-01", "split_manifest.json parses", True, True, True)
        check("SPL-MANIFEST-02", "Manifest strategy = temporal",
              "temporal", sm.get("strategy"), sm.get("strategy") == "temporal")
        check("SPL-MANIFEST-03", "Manifest status = locked",
              "locked", sm.get("status"), sm.get("status") == "locked")
        check("SPL-MANIFEST-04", "Manifest data_version matches",
              dv["data_version"], sm.get("data_version"), dv["data_version"] == sm.get("data_version"))

        # Row reconciliation
        recon = sm.get("row_reconciliation", {})
        check("SPL-RECON-01", "Row reconciliation match", True, recon.get("match"), recon.get("match") is True)
        check("SPL-RECON-02", "Total rows = source",
              recon.get("source"), recon.get("total"),
              recon.get("total") == recon.get("source"))
    else:
        check("SPL-MANIFEST-01", "split_manifest.json exists", True, False, False)

    # Split ID files
    split_files = {
        "train_ids.parquet": "SPL-FILE-TRAIN",
        "validation_ids.parquet": "SPL-FILE-VAL",
        "test_ids.parquet": "SPL-FILE-TEST",
        "split_version.txt": "SPL-FILE-VER",
        "test_set_lock.json": "SPL-FILE-LOCK",
    }
    for fname, cid in split_files.items():
        fpath = ROOT / "7.ML" / "7.4.splits" / fname
        check(cid, f"Split file exists: {fname}", True, fpath.exists(), fpath.exists())

    # Load split ID files and validate
    time_col = "release_year"
    train_ids_path = ROOT / "7.ML" / "7.4.splits" / "train_ids.parquet"
    val_ids_path = ROOT / "7.ML" / "7.4.splits" / "validation_ids.parquet"
    test_ids_path = ROOT / "7.ML" / "7.4.splits" / "test_ids.parquet"

    if all(p.exists() for p in [train_ids_path, val_ids_path, test_ids_path]):
        train_ids = pd.read_parquet(train_ids_path)
        val_ids = pd.read_parquet(val_ids_path)
        test_ids = pd.read_parquet(test_ids_path)

        # Hash verification
        train_hash = sha256_series(train_ids[id_col])
        val_hash = sha256_series(val_ids[id_col])
        test_hash = sha256_series(test_ids[id_col])

        if sm_path.exists():
            check("SPL-HASH-TRAIN", "Train ID hash matches manifest",
                  sm["train"]["id_sha256"][:16], train_hash[:16],
                  train_hash == sm["train"]["id_sha256"])
            check("SPL-HASH-VAL", "Val ID hash matches manifest",
                  sm["validation"]["id_sha256"][:16], val_hash[:16],
                  val_hash == sm["validation"]["id_sha256"])
            check("SPL-HASH-TEST", "Test ID hash matches manifest",
                  sm["test"]["id_sha256"][:16], test_hash[:16],
                  test_hash == sm["test"]["id_sha256"])

            # Row counts match manifest
            check("SPL-ROWS-TRAIN", "Train rows match manifest",
                  sm["train"]["rows"], len(train_ids),
                  sm["train"]["rows"] == len(train_ids))
            check("SPL-ROWS-VAL", "Val rows match manifest",
                  sm["validation"]["rows"], len(val_ids),
                  sm["validation"]["rows"] == len(val_ids))
            check("SPL-ROWS-TEST", "Test rows match manifest",
                  sm["test"]["rows"], len(test_ids),
                  sm["test"]["rows"] == len(test_ids))

        # Union = source
        all_split_ids = set(train_ids[id_col]) | set(val_ids[id_col]) | set(test_ids[id_col])
        source_ids = set(df[id_col])
        check("SPL-UNION-01", "Union of splits = source IDs",
              len(source_ids), len(all_split_ids),
              all_split_ids == source_ids)

        missing_ids = source_ids - all_split_ids
        extra_ids = all_split_ids - source_ids
        check("SPL-MISSING-01", "No missing IDs", 0, len(missing_ids), len(missing_ids) == 0)
        check("SPL-EXTRA-01", "No extra IDs", 0, len(extra_ids), len(extra_ids) == 0)

        # Intersection = 0
        tv = len(set(train_ids[id_col]) & set(val_ids[id_col]))
        tt = len(set(train_ids[id_col]) & set(test_ids[id_col]))
        vt = len(set(val_ids[id_col]) & set(test_ids[id_col]))
        check("SPL-INTERSECT-TV", "Train-Val intersection = 0", 0, tv, tv == 0)
        check("SPL-INTERSECT-TT", "Train-Test intersection = 0", 0, tt, tt == 0)
        check("SPL-INTERSECT-VT", "Val-Test intersection = 0", 0, vt, vt == 0)

        # Chronology via actual data
        train_data = df[df[id_col].isin(set(train_ids[id_col]))]
        val_data = df[df[id_col].isin(set(val_ids[id_col]))]
        test_data = df[df[id_col].isin(set(test_ids[id_col]))]

        t_max = int(train_data[time_col].max())
        v_min = int(val_data[time_col].min())
        v_max = int(val_data[time_col].max())
        te_min = int(test_data[time_col].min())

        check("SPL-CHRONO-01", "max(train) < min(val)",
              f"{t_max} < {v_min}", t_max < v_min, t_max < v_min)
        check("SPL-CHRONO-02", "max(val) < min(test)",
              f"{v_max} < {te_min}", v_max < te_min, v_max < te_min)

        # Temporal boundaries match config
        check("SPL-BOUND-01", "Train end matches config",
              sc["train"]["end_year"], t_max, sc["train"]["end_year"] == t_max)
        check("SPL-BOUND-02", "Val start matches config",
              sc["validation"]["start_year"], v_min, sc["validation"]["start_year"] == v_min)
        check("SPL-BOUND-03", "Test start matches config",
              sc["test"]["start_year"], te_min, sc["test"]["start_year"] == te_min)

    # ==============================================================
    # SECTION 10: Test set lock content validation
    # ==============================================================
    print("\n--- Test Set Lock Content Validation ---")
    lock_path = ROOT / "7.ML" / "7.4.splits" / "test_set_lock.json"
    if lock_path.exists():
        with open(lock_path, "r", encoding="utf-8") as f:
            lock = json.load(f)
        check("LOCK-CONTENT-01", "test_set_lock has data_version",
              True, "data_version" in lock, "data_version" in lock)
        check("LOCK-CONTENT-02", "test_set_lock has split_version",
              True, "split_version" in lock, "split_version" in lock)
        check("LOCK-CONTENT-03", "test_set_lock has test_ids_hash",
              True, "test_ids_hash" in lock, "test_ids_hash" in lock)
        check("LOCK-CONTENT-04", "test_set_lock has prohibited_actions",
              True, "prohibited_actions" in lock, "prohibited_actions" in lock)
        check("LOCK-CONTENT-05", "test_set_lock has descriptive_audit_performed",
              True, "descriptive_audit_performed" in lock, "descriptive_audit_performed" in lock)
        check("LOCK-CONTENT-06", "test_set_lock has lock_owner",
              True, "lock_owner" in lock, "lock_owner" in lock)

        # Hash match
        if test_ids_path.exists():
            check("LOCK-HASH-01", "Lock hash matches test_ids.parquet",
                  lock.get("test_ids_hash", "")[:16], test_hash[:16],
                  lock.get("test_ids_hash") == test_hash)

    # ==============================================================
    # SECTION 11: Legacy artifact quarantine check
    # ==============================================================
    print("\n--- Legacy Artifact Check ---")
    trained_dir = ROOT / "4.MODELS" / "4.1.trained"
    legacy_in_trained = []
    if trained_dir.exists():
        for f in trained_dir.glob("*.pkl"):
            legacy_in_trained.append(f.name)
        for f in trained_dir.glob("*.joblib"):
            legacy_in_trained.append(f.name)
    check("LEGACY-CLEAN-01", "No pkl/joblib in 4.1.trained",
          0, len(legacy_in_trained), len(legacy_in_trained) == 0,
          note=f"Found: {legacy_in_trained}" if legacy_in_trained else "")

    legacy_dir = ROOT / "4.MODELS" / "legacy_epic1"
    check("LEGACY-QUARANTINE-01", "legacy_epic1 directory exists",
          True, legacy_dir.exists(), legacy_dir.exists())
    if legacy_dir.exists():
        check("LEGACY-MANIFEST-01", "legacy_artifact_manifest.json exists",
              True, (legacy_dir / "legacy_artifact_manifest.json").exists(),
              (legacy_dir / "legacy_artifact_manifest.json").exists())
        check("LEGACY-DONOT-01", "DO_NOT_USE.md exists",
              True, (legacy_dir / "DO_NOT_USE.md").exists(),
              (legacy_dir / "DO_NOT_USE.md").exists())

    # ==============================================================
    # SECTION 12: Source reconciliation check
    # ==============================================================
    print("\n--- Source Reconciliation Check ---")
    sr_path = ROOT / "7.ML" / "7.3.data_intake" / "source_reconciliation.json"
    if sr_path.exists():
        with open(sr_path, "r", encoding="utf-8") as f:
            sr = json.load(f)
        check("RECON-FILE-01", "source_reconciliation.json exists and parses", True, True, True)
        check("RECON-STATUS-01", "Reconciliation status",
              "RECONCILED", sr.get("overall_status"), sr.get("overall_status") == "RECONCILED")
    else:
        check("RECON-FILE-01", "source_reconciliation.json exists", True, False, False)

    # ==============================================================
    # SECTION 13: Temporal shift profile check
    # ==============================================================
    print("\n--- Temporal Shift Profile Check ---")
    ts_path = ROOT / "7.ML" / "7.3.data_intake" / "temporal_shift_profile.json"
    if ts_path.exists():
        with open(ts_path, "r", encoding="utf-8") as f:
            ts = json.load(f)
        check("SHIFT-FILE-01", "temporal_shift_profile.json exists and parses", True, True, True)
        check("SHIFT-RISK-01", "Shift risks documented",
              True, bool(ts.get("risks")), bool(ts.get("risks")))
    else:
        check("SHIFT-FILE-01", "temporal_shift_profile.json exists", True, False, False)

    # ==============================================================
    # SUMMARY
    # ==============================================================
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    total_checks = len(results)

    print(f"\n{'=' * 70}")
    overall = "PASS_WITH_WARNINGS" if all_pass else "FAIL"
    print(f"VALIDATION: {total_checks} checks — {pass_count} PASS, {fail_count} FAIL")
    print(f"OVERALL STATUS: {overall}")
    print(f"{'=' * 70}")

    # Save results
    report = {
        "feature": "2.1",
        "hotfix": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": results,
        "total_checks": total_checks,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "overall_status": overall,
    }
    report_path = ROOT / "7.ML" / "7.3.data_intake" / "validation_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved: {report_path}")

    return results, overall


if __name__ == "__main__":
    results, status = main()
    sys.exit(0 if "PASS" in status else 1)
