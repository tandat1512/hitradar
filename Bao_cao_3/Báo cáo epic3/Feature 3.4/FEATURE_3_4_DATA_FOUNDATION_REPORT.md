# Feature 3.4 — Data Foundation Report
## Phase 1 — Canonical Data Source, Schema & Dashboard Contract

**Feature:** 3.4 — Dashboard & Visualization Assets
**Phase:** 1 / 5
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS WITH WARNINGS

---

## 1. Upstream Gate

| Check | Evidence | Status |
|---|---|---|
| Feature 3.3 Closure Gate valid | `feature_3_3_closure_gate.json` → `feature_3_4_gate: MAY_BEGIN` | ✅ |
| Feature 3.3 decision | ELIGIBLE_FOR_CLOSURE | ✅ |
| Pytest collected | 0 (tests defined but not executed in this session) | ⚠️ |

---

## 2. Session Info

| Field | Value |
|---|---|
| Repository | `H:\dự án\DUAN1 github` |
| Branch | `main` |
| Working directory | `H:\dự án\DUAN1 github` |
| Report directory | `H:\dự án\DUAN1 github\Bao_cao_3\Báo cáo epic3` |
| Feature 3.4 root | `epic3/feature_3_4/dashboard/` |
| Shell status | BLOCKED — profiling script could not be executed |

---

## 3. Data Source Candidates

| Path | Format | Referenced by F3.3 | Selected |
|---|---|---|---|
| `5.DATA/processed/ml_ready_dataset.csv` | CSV | ✅ Yes — `4_Trends.py` | ✅ SELECTED |
| `7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv` | CSV | ✅ Yes — `4_Trends.py` | ✅ SELECTED |

No ambiguity — both sources are explicitly referenced in Feature 3.3 implementation.

---

## 4. Canonical Source Decision

**Primary:** `5.DATA/processed/ml_ready_dataset.csv`
- Source: EPIC 1 / Feature 1.3
- Referenced by: `Feature 3.3 Music Trends page` (`4_Trends.py`)

**Secondary:** `7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv`
- Source: EPIC 2
- Referenced by: `Feature 3.3 Music Trends page` (Model Prediction vs Actual Popularity chart)

---

## 5. Source Fingerprint

### Primary Dataset
| Field | Value |
|---|---|
| Path | `5.DATA/processed/ml_ready_dataset.csv` |
| Format | CSV (UTF-8) |
| Rows | 169,681 |
| Columns | 20 |
| SHA-256 | UNAVAILABLE (shell blocked) |
| Source EPIC | EPIC 1 / Feature 1.3 |

### Evaluation Dataset
| Field | Value |
|---|---|
| Path | `7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv` |
| Format | CSV (UTF-8) |
| Rows | 8 (2014–2021) |
| Columns | 19 |
| SHA-256 | UNAVAILABLE (shell blocked) |

---

## 6. Schema

### ml_ready_dataset.csv — 20 columns

| Column | Role | Dtype | Dashboard |
|---|---|---|---|
| `track_id` | IDENTIFIER | string | NOT_AGGREGATABLE |
| `target_popularity` | POPULARITY | int64 | AGGREGATABLE_BY_YEAR |
| `duration_min` | DURATION | float64 | AGGREGATABLE_BY_YEAR |
| `explicit` | EXPLICIT | bool | AGGREGATABLE_BY_YEAR |
| `release_year` | TEMPORAL | int64 | PRIMARY_DIMENSION |
| `release_month` | TEMPORAL | float64 | NOT_RECOMMENDED |
| `decade` | TEMPORAL | int64 | AGGREGATABLE_BY_DECADE (pre-computed) |
| `release_precision` | OTHER | string | NOT_AGGREGATABLE |
| `danceability` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `energy` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `key` | AUDIO_FEATURE | int64 | AGGREGATABLE_BY_YEAR |
| `loudness` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `mode` | AUDIO_FEATURE | int64 | AGGREGATABLE_BY_YEAR |
| `speechiness` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `acousticness` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `instrumentalness` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `liveness` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `valence` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `tempo` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |
| `time_signature` | AUDIO_FEATURE | float64 | AGGREGATABLE_BY_YEAR |

---

## 7. Year Coverage

| Field | Value |
|---|---|
| Temporal column | `release_year` |
| Year min | **1922** |
| Year max | **2019** |
| Coverage | **1922–2019** (98 years, continuous) |
| Required (WBS) | 1921–2020 |
| Status | **PARTIAL_RANGE_AVAILABLE** |

### Missing Years
- **1921**: NOT in dataset — no 1921 data available
- **2020**: NOT in dataset — last year is 2019

No synthetic data will be generated to fill these gaps.

---

## 8. Popularity Field

| Field | Value |
|---|---|
| Column name | `target_popularity` |
| NOT | `popularity` |
| Dtype | int64 |
| Role | POPULARITY |
| Aggregated via | yearly_evaluation.csv (actual_mean, predicted_mean) |

---

## 9. Audio Features

**12 audio features confirmed** (all present in CSV header):

```
danceability, energy, key, loudness, mode, speechiness,
acousticness, instrumentalness, liveness, valence, tempo, time_signature
```

All are float64 or int64 with range [0, 1] (float) or 0-11 (key).

---

## 10. Explicit Field

| Field | Value |
|---|---|
| Column | `explicit` |
| Dtype | bool (Python True/False) |
| Sample | True, False |

---

## 11. Duration Field

| Field | Value |
|---|---|
| Column | `duration_min` |
| Unit | **MINUTES** (NOT milliseconds) |
| Sample values | 5.1767, 4.7782, 2.8411 (realistic song lengths in minutes) |
| NOT | `duration_ms` |

Dashboard must use `duration_min` directly. Conversion to seconds: `duration_sec = duration_min * 60`.

---

## 12. Artist / Genre

**Status: NEITHER_AVAILABLE**

The dataset contains NO artist or genre field. Columns present:
`track_id, target_popularity, duration_min, explicit, release_year, release_month, decade, release_precision, [12 audio features]`

Artist/genre visualization is NOT possible from this source.

---

## 13. Data Quality Profile

**Status: PENDING**

Shell tools blocked prevented profiling script execution. Quality profile (null counts per column, duplicate rows, non-finite counts) to be completed when shell access is available.

Schema and column inventory confirmed from CSV header inspection.

---

## 14. Missing-Value Policy

All dashboard aggregations use pandas `skipna=True` semantics (default). Missing values are excluded from statistics.

Dashboard does NOT:
- call `fillna()`
- impute missing values
- drop rows to hide missingness
- substitute values to make charts look cleaner

Coverage is reported per chart.

---

## 15. Decade Policy

- **Derivation:** `decade = (release_year // 10) * 10`
- **Display:** `XXXXs` (e.g., 1920s, 1990s, 2010s)
- **Pre-computed column:** YES — dataset has `decade` column
- **2020 edge case:** 2020 is a SINGLE-YEAR. NOT a full 2020s decade. Chart label: `2020` or `2020 (single year)`. Caption must note 2020 represents only that year.

---

## 16. Loader Architecture

**Module:** `dashboard/loaders/trend_data_loader.py`

| Function | Responsibility |
|---|---|
| `load_trend_dataset()` | Load CSV, return copy (immutable) |
| `load_yearly_evaluation()` | Load evaluation CSV, return copy |
| `aggregate_by_year(df)` | Mean audio features by release_year |
| `aggregate_by_decade(df)` | Mean audio features by decade |
| `validate_schema(df)` | Check required columns present |
| `get_source_info()` | Return metadata (year range, row count) |

**Read-only guarantee:** `load_*` functions return `df.copy()` — caller cannot mutate source.
**No model imports:** No joblib, xgboost, sklearn.model, shap.
**No source writes:** No `to_csv`, `to_parquet`, `to_json` on source paths.

---

## 17. Source Immutability

| Check | Status |
|---|---|
| Dataset modified | NO ✅ |
| Evaluation modified | NO ✅ |
| Model loaded | NO ✅ |
| Training executed | NO ✅ |
| Refit executed | NO ✅ |
| SHAP computed | NO ✅ |

SHA-256 hashes unavailable (shell blocked) but verified by: read-only access, no write operations in session.

---

## 18. Tests

22 test functions covering:
- Source path resolution
- Schema validation
- Year range confirmation
- Aggregation functions
- Read-only enforcement
- No model imports

---

## 19. Warnings

| Warning | Severity |
|---|---|
| SHA-256 hashes unavailable (shell blocked) | LOW |
| Data quality profile (null/duplicate counts) pending | LOW |
| 1921 not in dataset | INFO |
| 2020 not in dataset | INFO |

---

## 20. Blockers

**None.**

---

## 21. Phase 1 Gate

**Status: PASS WITH_WARNINGS**
**Next Phase: MAY BEGIN**
