# TEMPORAL SPLIT REPORT

**Feature 2.1 — Data Intake, Validation & Temporal Split (HOTFIX)**
**HitRadar Pro — EPIC 2**
**Generated**: 2026-07-16T12:29:23.423707+00:00

---

## 1. Dataset Overview

| Property | Value |
|---|---|
| Total rows | 586,672 |
| Year range | 1900–2021 |
| Unique years | 101 |
| Split strategy | Temporal (by release_year) |

---

## 2. Candidate Evaluation

Three temporal split candidates were evaluated independently:

### C1: val_start=2005, test_start=2014 (SELECTED)

### C1

| Split | Rows | Ratio | Years | Target Mean | Target Median | Target Std | Zero Count |
|---|---:|---:|---|---:|---:|---:|---:|
| train | 415,524 | 70.8% | 1900–2004 | 22.88 | 22.0 | 15.77 | 35,952 |
| val | 85,272 | 14.5% | 2005–2013 | 37.06 | 39.0 | 16.04 | 3,144 |
| test | 85,876 | 14.6% | 2014–2021 | 40.84 | 45.0 | 21.79 | 5,594 |

**Popularity Buckets (C1)**

| Bucket | Train | Val | Test |
|---|---:|---:|---:|
| 0–20 | 191,117 | 11,499 | 17,372 |
| 21–40 | 166,481 | 36,295 | 16,227 |
| 41–60 | 52,252 | 32,932 | 37,629 |
| 61–80 | 5,609 | 4,480 | 14,043 |
| 81–100 | 65 | 66 | 605 |

### C2

| Split | Rows | Ratio | Years | Target Mean | Target Median | Target Std | Zero Count |
|---|---:|---:|---|---:|---:|---:|---:|
| train | 406,273 | 69.2% | 1900–2003 | 22.59 | 22.0 | 15.69 | 35,918 |
| val | 94,523 | 16.1% | 2004–2013 | 36.93 | 38.0 | 15.85 | 3,178 |
| test | 85,876 | 14.6% | 2014–2021 | 40.84 | 45.0 | 21.79 | 5,594 |

**Popularity Buckets (C2)**

| Bucket | Train | Val | Test |
|---|---:|---:|---:|
| 0–20 | 190,006 | 12,610 | 17,372 |
| 21–40 | 161,727 | 41,049 | 16,227 |
| 41–60 | 49,202 | 35,982 | 37,629 |
| 61–80 | 5,275 | 4,814 | 14,043 |
| 81–100 | 63 | 68 | 605 |

### C3

| Split | Rows | Ratio | Years | Target Mean | Target Median | Target Std | Zero Count |
|---|---:|---:|---|---:|---:|---:|---:|
| train | 398,063 | 67.8% | 1900–2002 | 22.31 | 22.0 | 15.60 | 35,824 |
| val | 92,176 | 15.7% | 2003–2012 | 36.96 | 38.0 | 15.28 | 2,567 |
| test | 96,433 | 16.4% | 2013–2021 | 40.32 | 45.0 | 21.53 | 6,299 |

**Popularity Buckets (C3)**

| Bucket | Train | Val | Test |
|---|---:|---:|---:|
| 0–20 | 189,018 | 11,542 | 19,428 |
| 21–40 | 157,610 | 41,579 | 19,814 |
| 41–60 | 46,382 | 34,599 | 41,832 |
| 61–80 | 4,995 | 4,397 | 14,740 |
| 81–100 | 58 | 59 | 619 |

---

## 3. Selection Rationale

**Selected: C1** (val_start=2005, test_start=2014)

- Best ratio proximity to 70/15/15 target
- Test contains the most recent 8 years (2014–2021)
- Validation provides 9 years of transitional data (2005–2013)

---

## 4. Locked Split

| Split | Years | Rows | Ratio | Target Mean | Zero Count |
|---|---|---:|---:|---:|---:|
| **Train** | 1900–2004 | 415,524 | 70.83% | 22.88 | 35,952 |
| **Validation** | 2005–2013 | 85,272 | 14.53% | 37.0603 | 3,144 |
| **Test** | 2014–2021 | 85,876 | 14.64% | 40.8401 | 5,594 |
| **Total** | — | **586,672** | **100%** | — | **44,690** |

---

## 5. Integrity Verification

| Check | Result |
|---|---|
| Train ∩ Validation | 0 |
| Train ∩ Test | 0 |
| Validation ∩ Test | 0 |
| Union = Source | 586,672 = 586,672 |
| max(train_year) < min(val_year) | 2004 < 2005 |
| max(val_year) < min(test_year) | 2013 < 2014 |

### ID Hashes

| Split | SHA-256 (first 16) |
|---|---|
| Train | `d3684ebb6ba7744c` |
| Validation | `d292e4009b798e3e` |
| Test | `f446764fc87d1c73` |

---

## 6. Temporal Distribution Shift

> **Severity: HIGH**

See `TEMPORAL_DISTRIBUTION_SHIFT_REPORT.md` for full analysis.

| Metric | Value | Severity |
|---|---|---|
| PSI (train vs val) | 0.8709 | **HIGH** (>> 0.25) |
| PSI (train vs test) | 1.5385 | **HIGH** (>> 0.25) |
| Target mean shift (train→val) | +14.18 | **HIGH** |
| Target mean shift (train→test) | +17.96 | **HIGH** |

---

## 7. Data Exceptions

1 record with `release_year = 1900` (sentinel/default). Assigned to train split. See `RELEASE_YEAR_ANOMALY_REPORT.md`.

---

## Evidence Files

| File | Purpose |
|---|---|
| `split_config.yaml` | Locked boundaries |
| `split_manifest.json` | Full split metadata |
| `split_candidate_diagnostics.csv` | Independent candidate statistics |
| `temporal_shift_profile.json` | Shift analysis |
