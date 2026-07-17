# RELEASE YEAR ANOMALY REPORT

**Feature 2.1 HOTFIX — HitRadar Pro EPIC 2**

---

## 1. Issue Summary

| Property | Value |
|---|---|
| **Anomaly** | 1 record with `release_year = 1900` |
| **EPIC 1 documented range** | 1921–2021 (feature_dictionary.md, DATA_DICTIONARY.md) |
| **Actual range** | 1900–2021 |
| **Contract deviation** | YES |
| **Severity** | LOW (1 / 586,672 = 0.00017%) |

---

## 2. Affected Record

| Column | Value |
|---|---|
| track_id | `74CSJTE5QQp1e4bHzm3wti` |
| target_popularity | 19 |
| duration_min | 3.8987 |
| explicit | False |
| release_year | **1900** |
| release_month | 1.0 |
| decade | 1900 |
| release_precision | **day** |
| danceability | 0.659 |
| energy | 0.791 |
| key | 2 |
| loudness | -4.895 |
| mode | 1 |
| speechiness | 0.0295 |
| acousticness | 0.139 |
| instrumentalness | 1.63e-06 |
| liveness | 0.161 |
| valence | 0.956 |
| tempo | 141.999 |
| time_signature | 4.0 |

---

## 3. Cross-Source Verification

| Source | release_year | Present | Match |
|---|---|---|---|
| Parquet (`ml_ready_dataset.parquet`) | 1900 | Yes | — |
| CSV (`ml_ready_dataset.csv`) | 1900 | Yes | Match |
| Database view (inferred from exports) | 1900 | Yes | Match |

Both Parquet and CSV contain the same record with identical values across all 20 columns.

---

## 4. Root Cause Analysis

### Evidence

1. `release_precision = "day"` — Spotify reported day-level precision
2. `release_month = 1.0` — Month is January
3. Combining: the original `release_date` was likely `"1900-01-01"`
4. Year 1900 is NOT a valid music release year for a Spotify track with modern audio features (energy=0.791, danceability=0.659)
5. No other years between 1900 and 1922 exist — a 22-year gap
6. Next earliest year is 1922 (294 tracks)

### Conclusion

**Classification: C — SENTINEL / DEFAULT VALUE**

`release_date = "1900-01-01"` is a known Spotify API default for tracks where the actual release date is unknown or not properly catalogued. The Spotify metadata system uses this as a sentinel value.

The track exists on Spotify with `target_popularity = 19` (non-zero), has standard modern audio features, and the `release_precision = "day"` is contradictory (day precision for a date that is clearly a placeholder).

### Why EPIC 1 Documentation Says 1921–2021

EPIC 1 `clean.tracks` documentation states: `release_year (observed 1921–2021)`. This could mean:
- A. EPIC 1 cleaning logic filtered year=1900 from `clean.tracks` but the ML view re-included it
- B. EPIC 1 documentation was computed on a subset or at a different pipeline stage
- C. The year-1900 record was present but overlooked in the documented range

Based on the evidence, the most likely explanation is **B or C** — the feature_dictionary.md was written during a profiling step that may have filtered sentinel values, but the `vw_ml_ready_dataset` view includes all rows from `clean.tracks` without filtering.

---

## 5. Impact Assessment

| Dimension | Impact |
|---|---|
| Row count | 1 / 586,672 (0.00017%) — negligible |
| Split assignment | Assigned to train (year < 2005) |
| Model training | Negligible — 1 row in 415,524 train rows |
| Target distribution | No measurable effect |
| Split boundaries | No change needed |
| Reproducibility | No effect |

---

## 6. Decision

**KEEP_WITH_EXCEPTION** — Record is retained in the dataset with a formal exception registered in `data_exceptions.json`.

### Rationale
1. Removing 1 row would require creating a new data version, new hashes, and new split IDs — disproportionate effort for negligible impact.
2. The record's audio features and popularity are valid; only the release date is a sentinel.
3. The record is in the train split where it has no meaningful influence on model evaluation.

### Actions Taken
- Registered in `7.ML/7.3.data_intake/data_exceptions.json` as EXC-001
- Added to split_manifest.json under `data_exceptions`
- Validation script includes year-range check with exception registry

---

## 7. Recommendations

| Action | Owner | Priority |
|---|---|---|
| Update EPIC 1 feature_dictionary.md to note actual range includes 1900 | EPIC 1 owner (Đạt) | LOW |
| Update DATA_DICTIONARY.md clean.tracks note from "1921–2021" to "1900–2021 (1900 is sentinel)" | EPIC 1 owner (Đạt) | LOW |
| No dataset regeneration needed | — | — |
| No split boundary change needed | — | — |

---

## 8. Evidence Files

| File | Purpose |
|---|---|
| `7.ML/7.3.data_intake/data_exceptions.json` | Formal exception registry |
| `7.ML/7.3.data_intake/hotfix_investigation_results.json` | Full investigation data |
| `7.ML/7.3.data_intake/year_distribution.csv` | Year-level row counts |
