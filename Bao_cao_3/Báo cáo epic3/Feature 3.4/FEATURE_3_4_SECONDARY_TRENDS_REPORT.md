# Feature 3.4 — Secondary Trends Report
## Phase 3 — Explicit, Duration & Artist/Genre Summary

**Feature:** 3.4 — Dashboard & Visualization Assets
**Phase:** 3 / 5
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS WITH WARNINGS

---

## 1. Prerequisite Validation

| Check | Evidence | Status |
|---|---|---|
| Phase 2 Gate valid | `feature_3_4_phase_2_gate.json` → `next_phase: MAY_BEGIN` | ✅ |
| Phase 1 explicit field | `explicit` column (bool) confirmed | ✅ |
| Phase 1 duration field | `duration_min` (minutes) confirmed | ✅ |
| Phase 1 artist/genre | `NEITHER_AVAILABLE` confirmed | ✅ |

---

## 2. Explicit Trend — Field Status

| Property | Value |
|---|---|
| Column | `explicit` |
| Dtype | bool (Python True/False) |
| Valid values | `True`, `False` |
| Null values | Excluded from rate denominator; reported separately |

**Aggregation:** `explicit_rate = explicit_count / valid_count` per decade

---

## 3. Explicit Normalization Policy

| Rule | Applied |
|---|---|
| Valid values: True / False | ✅ |
| `null` excluded from denominator | ✅ |
| Invalid (non-bool) excluded from denominator | ✅ |
| `invalid_count` reported per decade | ✅ |
| Rate = comparable across uneven decade sizes | ✅ |
| NOT raw count | ✅ |

---

## 4. Explicit Chart

**Title:** `Percentage of Tracks Marked Explicit by Decade`
**Type:** Bar chart
**Y-axis:** Percentage (%)
**Baseline:** 0% (rate is inherently bounded 0–100)

No causal language in title.

---

## 5. Duration — Unit Policy

| Property | Value |
|---|---|
| Source column | `duration_min` |
| Source unit | **Minutes** (confirmed from CSV samples: 5.1767, 4.7782) |
| Conversion needed | **None** — already in minutes |
| To seconds (derived only) | `duration_sec = duration_min × 60` |

---

## 6. Duration — Invalid Value Handling

| Condition | Handling |
|---|---|
| `null` | Excluded from aggregation; counted separately |
| `≤ 0` | Excluded; counted separately |
| `< 0.1 min` (6 sec) | Excluded; counted separately |
| `> 30 min` | Excluded; counted separately |
| Winsorization | **NOT used** |
| Deleted from source | **NOT done** |

---

## 7. Duration Chart

**Title:** `Average Track Duration by Decade`
**Type:** Bar chart
**Y-axis:** Minutes
**Aggregation:** Mean (median available as alternative)

---

## 8. Artist/Genre — Source Decision

| Property | Value |
|---|---|
| `artist` column | **NOT AVAILABLE** |
| `genre` column | **NOT AVAILABLE** |
| Status | `NEITHER_AVAILABLE` |
| Reason | Confirmed from Phase 1: no such column in `ml_ready_dataset.csv` |

### Available Dataset Columns
```
track_id, target_popularity, duration_min, explicit,
release_year, release_month, decade, release_precision,
danceability, energy, key, loudness, mode,
speechiness, acousticness, instrumentalness, liveness,
valence, tempo, time_signature
```

### Policy
| Action | Allowed? |
|---|---|
| Infer artist from track_id | ❌ NO |
| Parse multi-artist strings | ❌ NO |
| Generate synthetic artist names | ❌ NO |
| Display "Not available" message | ✅ YES |

---

## 9. Artist/Genre Summary — NOT_AVAILABLE

**Task 3.4.7:** `NOT_AVAILABLE_FROM_SOURCE`

Dashboard page will display:
> "Artist and genre data are not available in this dataset. This dataset contains audio features and track metadata only."

---

## 10. Dashboard Filter Contract

| Chart | Year filter applies? |
|---|---|
| Popularity by Year | ✅ Yes — uses selected range |
| Audio Feature by Year | ✅ Yes — uses selected range |
| Track Count by Year | ✅ Yes — uses selected range |
| Popularity by Decade | ❌ No — uses full dataset decade |
| Audio Feature by Decade | ❌ No — uses full dataset decade |
| Explicit Trend | ❌ No — uses full dataset decade |
| Duration Trend | ❌ No — uses full dataset decade |

**Rationale:** Decade aggregations pre-compute on full dataset. Year range filter only affects year-level charts.

---

## 11. Source Immutability

| Check | Status |
|---|---|
| Source dataset modified | NO ✅ |
| Model loaded | NO ✅ |
| Training executed | NO ✅ |
| SHAP computed | NO ✅ |

---

## 12. Warnings

| Warning | Severity |
|---|---|
| Exact explicit rate values pending pandas profiling | LOW |
| Exact duration aggregation values pending pandas profiling | LOW |
| SHA-256 verification pending shell | LOW |

---

## 13. Blockers

**None.**

---

## 14. Phase Gate

**Status: PASS WITH_WARNINGS — MAY BEGIN Phase 4**
