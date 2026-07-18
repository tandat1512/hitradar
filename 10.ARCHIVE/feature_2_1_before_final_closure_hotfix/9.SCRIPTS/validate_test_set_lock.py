#!/usr/bin/env python3
"""
HOTFIX 4 — Test Set Lock Guard Script
Validates test_set_lock.json integrity and checks for test misuse.
"""

import json
import hashlib
import sys
from pathlib import Path

import yaml
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent

def sha256_series(series):
    h = hashlib.sha256()
    for val in sorted(series.astype(str).values):
        h.update(val.encode("utf-8"))
    return h.hexdigest()

def main():
    print("=" * 70)
    print("VALIDATE TEST SET LOCK — Feature 2.1 Guard")
    print("=" * 70)

    results = []
    all_pass = True

    def check(cid, desc, expected, actual, pass_cond, note=""):
        nonlocal all_pass
        status = "PASS" if pass_cond else "FAIL"
        if not pass_cond:
            all_pass = False
        results.append({"check_id": cid, "description": desc, "status": status, "note": note})
        mark = "PASS" if pass_cond else "FAIL"
        print(f"  [{cid}] {desc}: {mark}")

    # 1. test_set_lock.json exists and parses
    lock_path = ROOT / "7.ML" / "7.4.splits" / "test_set_lock.json"
    check("LOCK-FILE-01", "test_set_lock.json exists", True, lock_path.exists(), lock_path.exists())

    if not lock_path.exists():
        print("FATAL: Cannot continue without test_set_lock.json")
        return results, "FAIL"

    with open(lock_path, "r", encoding="utf-8") as f:
        lock = json.load(f)
    check("LOCK-PARSE-01", "test_set_lock.json parses", True, True, True)

    # 2. Required keys
    required_keys = [
        "status", "data_version", "split_version", "test_ids_hash",
        "test_row_count", "lock_timestamp", "lock_owner",
        "permitted_stage", "prohibited_actions",
        "descriptive_audit_performed", "descriptive_audit_fields",
        "final_evaluation_status",
    ]
    for key in required_keys:
        present = key in lock
        check(f"LOCK-KEY-{key[:8].upper()}", f"Required key: {key}", True, present, present)

    # 3. Status is locked
    check("LOCK-STATUS-01", "Lock status is 'locked'", "locked", lock.get("status"),
          lock.get("status") == "locked")

    # 4. Data version matches
    dv_path = ROOT / "7.ML" / "7.3.data_intake" / "data_version.json"
    if dv_path.exists():
        with open(dv_path, "r", encoding="utf-8") as f:
            dv = json.load(f)
        check("LOCK-DV-01", "data_version matches data_version.json",
              dv["data_version"], lock.get("data_version"),
              dv["data_version"] == lock.get("data_version"))

    # 5. Split version matches
    sv_path = ROOT / "7.ML" / "7.4.splits" / "split_version.txt"
    if sv_path.exists():
        sv = sv_path.read_text(encoding="utf-8").strip()
        check("LOCK-SV-01", "split_version matches split_version.txt",
              sv, lock.get("split_version"), sv == lock.get("split_version"))

    # 6. Test ID hash matches actual test_ids.parquet
    test_ids_path = ROOT / "7.ML" / "7.4.splits" / "test_ids.parquet"
    if test_ids_path.exists():
        test_ids_df = pd.read_parquet(test_ids_path)
        actual_hash = sha256_series(test_ids_df["track_id"])
        check("LOCK-HASH-01", "test_ids_hash matches test_ids.parquet",
              lock.get("test_ids_hash", "")[:16], actual_hash[:16],
              actual_hash == lock.get("test_ids_hash"))
        check("LOCK-ROWS-01", "test_row_count matches test_ids.parquet",
              lock.get("test_row_count"), len(test_ids_df),
              lock.get("test_row_count") == len(test_ids_df))

    # 7. No model metrics files for test before Feature 2.5
    eval_dir = ROOT / "4.MODELS" / "4.2.evaluation"
    test_metric_files = []
    if eval_dir.exists():
        for f in eval_dir.glob("*test*"):
            test_metric_files.append(f.name)
        for f in eval_dir.glob("*final_eval*"):
            test_metric_files.append(f.name)
    check("LOCK-MISUSE-01", "No test metric files before Feature 2.5",
          0, len(test_metric_files), len(test_metric_files) == 0,
          note=f"Found: {test_metric_files}" if test_metric_files else "")

    # 8. Check Feature 2.2-2.4 scripts don't load y_test
    scripts_dir = ROOT / "9.SCRIPTS"
    misuse_scripts = []
    for script_file in scripts_dir.glob("*.py"):
        # Only check feature_2_2, 2_3, 2_4 scripts
        name = script_file.name.lower()
        if any(x in name for x in ["feature_2_2", "feature_2_3", "feature_2_4",
                                     "2.2", "2.3", "2.4"]):
            try:
                content = script_file.read_text(encoding="utf-8", errors="ignore")
                suspicious = []
                if "y_test" in content:
                    suspicious.append("y_test reference")
                if "test_df[" in content and "target_popularity" in content:
                    suspicious.append("test_df target access")
                if suspicious:
                    misuse_scripts.append({"script": script_file.name, "issues": suspicious})
            except Exception:
                pass
    check("LOCK-MISUSE-02", "No Feature 2.2-2.4 scripts access y_test",
          0, len(misuse_scripts), len(misuse_scripts) == 0,
          note=str(misuse_scripts) if misuse_scripts else "")

    # 9. Descriptive audit properly documented
    check("LOCK-AUDIT-01", "Descriptive audit flag set",
          True, lock.get("descriptive_audit_performed"),
          lock.get("descriptive_audit_performed") is True)
    check("LOCK-AUDIT-02", "Descriptive audit fields listed",
          True, bool(lock.get("descriptive_audit_fields")),
          bool(lock.get("descriptive_audit_fields")))

    # 10. Final evaluation not started
    check("LOCK-EVAL-01", "Final evaluation not started",
          "NOT_STARTED", lock.get("final_evaluation_status"),
          lock.get("final_evaluation_status") == "NOT_STARTED")

    # 11. No model metrics on test
    check("LOCK-EVAL-02", "No model metrics on test",
          None, lock.get("model_metrics_on_test"),
          lock.get("model_metrics_on_test") is None)

    # Summary
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")

    print(f"\n{'=' * 70}")
    overall = "PASS" if all_pass else "FAIL"
    print(f"TEST SET LOCK VALIDATION: {pass_count} PASS, {fail_count} FAIL — {overall}")
    print(f"{'=' * 70}")

    return results, overall


if __name__ == "__main__":
    results, status = main()
    sys.exit(0 if status == "PASS" else 1)
