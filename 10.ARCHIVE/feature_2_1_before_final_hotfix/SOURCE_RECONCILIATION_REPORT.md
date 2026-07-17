# SOURCE RECONCILIATION REPORT

**Feature 2.1 HOTFIX — HitRadar Pro EPIC 2**

---

## 1. Purpose

Reconcile the frozen physical snapshot (`ml_ready_dataset.parquet`) with the logical authoritative source (`analytics.vw_ml_ready_dataset`) to verify they represent identical data.

---

## 2. Source Definitions

| Role | Source | Path |
|---|---|---|
| **Logical authoritative** | `analytics.vw_ml_ready_dataset` | Database view |
| **Frozen physical snapshot (primary)** | `ml_ready_dataset.parquet` | `5.DATA/processed/ml_ready_dataset.parquet` |
| **Frozen physical snapshot (fallback)** | `ml_ready_dataset.csv` | `5.DATA/processed/ml_ready_dataset.csv` |

Both Parquet and CSV were exported from the same database view by EPIC 1 Feature 1.8. The Parquet file is used as the primary input for Feature 2.1 ML pipeline. The CSV serves as fallback verification.

---

## 3. Reconciliation Results

### Row and Column Match

| Property | Parquet | CSV | Match |
|---|---|---|---|
| Row count | 586,672 | 586,672 | ✓ |
| Column count | 20 | 20 | ✓ |
| Column names | Identical | Identical | ✓ |
| Column order | Identical | Identical | ✓ |

### NULL Count Comparison

| Column | Parquet NULLs | CSV NULLs | Match |
|---|---|---|---|
| release_month | 136,489 | 136,489 | ✓ |
| tempo | 328 | 328 | ✓ |
| time_signature | 337 | 337 | ✓ |
| All other columns | 0 | 0 | ✓ |

### Identity and Target Verification

| Check | Result |
|---|---|
| Track ID set match | ✓ MATCH |
| Parquet-only IDs | 0 |
| CSV-only IDs | 0 |
| Sorted track_id hash match | ✓ MATCH |
| Target mean (Parquet) | 27.570053 |
| Target mean (CSV) | 27.570053 |
| Target mean match | ✓ MATCH |
| Numeric values match (all columns) | ✓ MATCH |

### File Fingerprints

| File | SHA-256 | Size |
|---|---|---|
| ml_ready_dataset.parquet | (see source_reconciliation.json) | 25.21 MB |
| ml_ready_dataset.csv | (see source_reconciliation.json) | 69.19 MB |

---

## 4. Reconciliation Status

**RECONCILED** — Parquet and CSV contain identical data.

---

## 5. Limitation

Direct comparison with the live database view (`analytics.vw_ml_ready_dataset`) requires database connectivity, which is not available in the ML script environment. Reconciliation is performed between the two physical exports. Both were produced by EPIC 1 Feature 1.8 export scripts and validated at handoff.

---

## 6. Evidence Files

| File | Purpose |
|---|---|
| `7.ML/7.3.data_intake/source_reconciliation.json` | Machine-readable reconciliation results |
| `7.ML/7.3.data_intake/data_version.json` | Frozen data version with file hash |
