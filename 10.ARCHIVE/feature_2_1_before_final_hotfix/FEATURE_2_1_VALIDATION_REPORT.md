# FEATURE 2.1 VALIDATION REPORT

**Feature 2.1 — Data Intake, Validation & Temporal Split (HOTFIX)**
**HitRadar Pro — EPIC 2**
**Generated**: 2026-07-16T12:29:23.423707+00:00

---

## Overall Status: PASS_WITH_WARNINGS

**93 checks total — 93 PASS, 0 FAIL**

---

## Validation Checks

| # | Check ID | Description | Status |
|---|---|---|---|
| 1 | F20-PREREQ-01 | Feature 2.0: EPIC2_SCOPE_LOCK.md | PASS |
| 2 | F20-PREREQ-02 | Feature 2.0: ML_CONTRACT.md | PASS |
| 3 | F20-PREREQ-03 | Feature 2.0: EXPERIMENT_DESIGN.md | PASS |
| 4 | F20-PREREQ-04 | Feature 2.0: experiment_config.yaml | PASS |
| 5 | F20-PREREQ-05 | Feature 2.0: EPIC2_DEFINITION_OF_DONE.md | PASS |
| 6 | F20-PREREQ-06 | Feature 2.0: FEATURE_2_0_COMPLETION_REPORT.md | PASS |
| 7 | CFG-PARSE-01 | experiment_config.yaml parses | PASS |
| 8 | CFG-KEY-PROJE | Config has key: project | PASS |
| 9 | CFG-KEY-DATA | Config has key: data | PASS |
| 10 | CFG-KEY-SPLIT | Config has key: split | PASS |
| 11 | CFG-KEY-LEAKA | Config has key: leakage_rules | PASS |
| 12 | CFG-KEY-REPRO | Config has key: reproducibility | PASS |
| 13 | CFG-PARSE-02 | split_config.yaml parses | PASS |
| 14 | CFG-SPLIT-01 | Split strategy = temporal | PASS |
| 15 | CFG-SPLIT-02 | Split status = locked | PASS |
| 16 | DV-PARSE-01 | data_version.json parses | PASS |
| 17 | DV-KEY-DATA_V | data_version has key: data_version | PASS |
| 18 | DV-KEY-ACTUAL | data_version has key: actual_source_used | PASS |
| 19 | DV-KEY-ROWS | data_version has key: rows | PASS |
| 20 | DV-KEY-COLUMN | data_version has key: columns | PASS |
| 21 | DV-KEY-FILE_S | data_version has key: file_sha256 | PASS |
| 22 | DV-KEY-SCHEMA | data_version has key: schema_hash | PASS |
| 23 | DV-ROWS-01 | data_version rows = 586672 | PASS |
| 24 | DV-COLS-01 | data_version cols = 20 | PASS |
| 25 | DV-HASH-01 | File SHA-256 matches frozen hash | PASS |
| 26 | DATA-ROWS-01 | Row count = 586672 | PASS |
| 27 | DATA-COLS-01 | Column count = 20 | PASS |
| 28 | DATA-SCHEMA-01 | All 20 official columns present | PASS |
| 29 | DATA-LEAK-01 | No forbidden leakage columns in features | PASS |
| 30 | DATA-LEAK-02 | target_popularity not in features | PASS |
| 31 | DATA-LEAK-03 | track_id not in features | PASS |
| 32 | ID-NULL-01 | track_id NULL count | PASS |
| 33 | ID-DUP-01 | track_id duplicate count | PASS |
| 34 | TGT-NULL-01 | target NULL count | PASS |
| 35 | TGT-NAN-01 | target NaN count | PASS |
| 36 | TGT-INF-01 | target infinite count | PASS |
| 37 | TGT-MIN-01 | target min >= 0 | PASS |
| 38 | TGT-MAX-01 | target max <= 100 | PASS |
| 39 | SPLIT-RY-NULL-01 | release_year NULL count (for split) | PASS |
| 40 | EXC-FILE-01 | data_exceptions.json exists and parses | PASS |
| 41 | EXC-YEAR1900-01 | Year 1900 anomaly registered in exceptions | PASS |
| 42 | SS-PARSE-01 | schema_snapshot.json parses | PASS |
| 43 | SS-COLS-01 | schema_snapshot column count | PASS |
| 44 | SS-DV-01 | schema_snapshot data_version matches | PASS |
| 45 | IM-PARSE-01 | input_manifest.json parses | PASS |
| 46 | IM-ROWS-01 | input_manifest actual_rows matches | PASS |
| 47 | IM-HASH-01 | input_manifest schema_hash matches data_version | PASS |
| 48 | TP-PARSE-01 | target_profile.json parses | PASS |
| 49 | TP-COUNT-01 | target_profile count | PASS |
| 50 | TP-NULL-01 | target_profile null_count | PASS |
| 51 | SPL-MANIFEST-01 | split_manifest.json parses | PASS |
| 52 | SPL-MANIFEST-02 | Manifest strategy = temporal | PASS |
| 53 | SPL-MANIFEST-03 | Manifest status = locked | PASS |
| 54 | SPL-MANIFEST-04 | Manifest data_version matches | PASS |
| 55 | SPL-RECON-01 | Row reconciliation match | PASS |
| 56 | SPL-RECON-02 | Total rows = source | PASS |
| 57 | SPL-FILE-TRAIN | Split file exists: train_ids.parquet | PASS |
| 58 | SPL-FILE-VAL | Split file exists: validation_ids.parquet | PASS |
| 59 | SPL-FILE-TEST | Split file exists: test_ids.parquet | PASS |
| 60 | SPL-FILE-VER | Split file exists: split_version.txt | PASS |
| 61 | SPL-FILE-LOCK | Split file exists: test_set_lock.json | PASS |
| 62 | SPL-HASH-TRAIN | Train ID hash matches manifest | PASS |
| 63 | SPL-HASH-VAL | Val ID hash matches manifest | PASS |
| 64 | SPL-HASH-TEST | Test ID hash matches manifest | PASS |
| 65 | SPL-ROWS-TRAIN | Train rows match manifest | PASS |
| 66 | SPL-ROWS-VAL | Val rows match manifest | PASS |
| 67 | SPL-ROWS-TEST | Test rows match manifest | PASS |
| 68 | SPL-UNION-01 | Union of splits = source IDs | PASS |
| 69 | SPL-MISSING-01 | No missing IDs | PASS |
| 70 | SPL-EXTRA-01 | No extra IDs | PASS |
| 71 | SPL-INTERSECT-TV | Train-Val intersection = 0 | PASS |
| 72 | SPL-INTERSECT-TT | Train-Test intersection = 0 | PASS |
| 73 | SPL-INTERSECT-VT | Val-Test intersection = 0 | PASS |
| 74 | SPL-CHRONO-01 | max(train) < min(val) | PASS |
| 75 | SPL-CHRONO-02 | max(val) < min(test) | PASS |
| 76 | SPL-BOUND-01 | Train end matches config | PASS |
| 77 | SPL-BOUND-02 | Val start matches config | PASS |
| 78 | SPL-BOUND-03 | Test start matches config | PASS |
| 79 | LOCK-CONTENT-01 | test_set_lock has data_version | PASS |
| 80 | LOCK-CONTENT-02 | test_set_lock has split_version | PASS |
| 81 | LOCK-CONTENT-03 | test_set_lock has test_ids_hash | PASS |
| 82 | LOCK-CONTENT-04 | test_set_lock has prohibited_actions | PASS |
| 83 | LOCK-CONTENT-05 | test_set_lock has descriptive_audit_performed | PASS |
| 84 | LOCK-CONTENT-06 | test_set_lock has lock_owner | PASS |
| 85 | LOCK-HASH-01 | Lock hash matches test_ids.parquet | PASS |
| 86 | LEGACY-CLEAN-01 | No pkl/joblib in 4.1.trained | PASS |
| 87 | LEGACY-QUARANTINE-01 | legacy_epic1 directory exists | PASS |
| 88 | LEGACY-MANIFEST-01 | legacy_artifact_manifest.json exists | PASS |
| 89 | LEGACY-DONOT-01 | DO_NOT_USE.md exists | PASS |
| 90 | RECON-FILE-01 | source_reconciliation.json exists and parses | PASS |
| 91 | RECON-STATUS-01 | Reconciliation status | PASS |
| 92 | SHIFT-FILE-01 | temporal_shift_profile.json exists and parses | PASS |
| 93 | SHIFT-RISK-01 | Shift risks documented | PASS |

---

## Check Coverage

| Section | Checks | Description |
|---|---:|---|
| Feature 2.0 Prerequisites | 6 | Contract files exist |
| Config Content | 9 | YAML parse + required keys |
| Data Version Content | 9 | JSON parse + keys + hash verification |
| Dataset Validation | 12 | Schema, leakage, identifier, target |
| Data Exceptions | 2 | Exception registry + year 1900 |
| Schema Snapshot | 3 | Content + data version match |
| Input Manifest | 3 | Content + row count + hash |
| Target Profile | 3 | Content + count + nulls |
| Split Artifacts | 22 | Manifest, files, hashes, union, intersection, chronology, bounds |
| Test Set Lock | 7 | Content + governance keys + hash |
| Legacy Artifacts | 4 | Quarantine + manifest |
| Source Reconciliation | 2 | File + status |
| Temporal Shift | 2 | File + risks |
| **Total** | **93** | — |

---

## Notes

- Validation upgraded from file-existence to content-level semantic validation (HOTFIX 6)
- All check IDs are unique and descriptive
- Temporal shift documented as HIGH severity, not "expected warning"
- Year 1900 registered as formal exception, not silently ignored
- Test set governance documented per HOTFIX 4 semantics
- Legacy .pkl files quarantined and validated

---

## Evidence Files

| File | Purpose |
|---|---|
| `validation_results.json` | Machine-readable check results |
| `validate_feature_2_1.py` | Validation script (93 checks) |
| `validate_test_set_lock.py` | Test set guard script |
| `validate_temporal_split.py` | Split integrity script |
