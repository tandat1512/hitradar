# DATA INTAKE VALIDATION REPORT

**Feature 2.1 — Data Intake, Validation & Temporal Split (HOTFIX)**
**HitRadar Pro — EPIC 2**
**Generated**: 2026-07-16T12:29:23.423707+00:00

---

## 1. Source

| Property | Value |
|---|---|
| Logical authoritative source | `analytics.vw_ml_ready_dataset` |
| Frozen physical snapshot | `5.DATA/processed/ml_ready_dataset.parquet` |
| Data version | `ml-ready-2026-07-16-v1` |
| File SHA-256 | `be198ad6303400534dc455e334ee4d9f...` |
| Source reconciliation (Parquet vs CSV) | **RECONCILED** |

---

## 2. Schema

| Check | Expected | Actual | Status |
|---|---|---|---|
| Row count | 586,672 | 586,672 | PASS |
| Column count | 20 | 20 | PASS |
| Baseline input features | 18 | 18 | PASS |
| target_popularity in features | No | No | PASS |
| track_id in features | No | No | PASS |
| Forbidden leakage columns | 0 | 0 | PASS |

---

## 3. Identifier — track_id

| Check | Value | Status |
|---|---|---|
| NULL count | 0 | PASS |
| Duplicate count | 0 | PASS |
| Unique count | 586,672 | PASS |

---

## 4. Target — target_popularity

| Check | Value | Status |
|---|---|---|
| NULL count | 0 | PASS |
| Min | 0 | PASS |
| Max | 100 | PASS |
| Mean | 27.5701 | — |
| Median | 27.0 | — |
| Std | 18.3706 | — |
| Zero count | 44,690 (7.62%) | WARNING |

---

## 5. Warning Profile

| Warning | Count | Status | Match EPIC 1 |
|---|---:|---|---|
| tempo NULL | 328 | EXPECTED_WARNING | Match (328) |
| time_signature NULL | 337 | EXPECTED_WARNING | Match (337) |
| release_month NULL | 136,489 | EXPECTED_WARNING | Match (136,489) |

---

## 6. Data Exceptions

| Exception ID | Track ID | Field | Value | Classification |
|---|---|---|---|---|
| EXC-001 | `74CSJTE5QQp1e4bHzm3wti` | release_year | 1900 | SENTINEL_OR_DEFAULT |

---

## 7. Contract Deviations

| Deviation | Documented | Actual | Resolution |
|---|---|---|---|
| release_year min | 1921 | 1900 | Registered as exception EXC-001. See RELEASE_YEAR_ANOMALY_REPORT.md |

---

## 8. Validation Summary

| Result | Value |
|---|---|
| Total checks | 93 |
| PASS | 93 |
| FAIL | 0 |
| Overall | PASS_WITH_WARNINGS |

---

## Evidence Files

| File | Purpose |
|---|---|
| `data_version.json` | Frozen data version |
| `schema_snapshot.json` | Column types |
| `input_manifest.json` | Source metadata |
| `target_profile.json` | Target statistics |
| `warning_profile.json` | Warning baseline |
| `source_reconciliation.json` | Parquet vs CSV |
| `data_exceptions.json` | Formal exceptions |
| `validation_results.json` | All check results |
