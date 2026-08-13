# Feature 3.4 — Popularity & Audio Feature Trends Report
## Phase 2 — Aggregation Engine, Chart Contracts & Visualization

**Feature:** 3.4 — Dashboard & Visualization Assets
**Phase:** 2 / 5
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS WITH WARNINGS

---

## 1. Prerequisite Validation

| Check | Evidence | Status |
|---|---|---|
| Phase 1 Gate valid | `feature_3_4_phase_1_gate.json` → `next_phase: MAY_BEGIN` | ✅ |
| Canonical source confirmed | `5.DATA/processed/ml_ready_dataset.csv` | ✅ |
| Phase 1 status | PASS_WITH_WARNINGS | ✅ |

---

## 2. Architecture

```
dashboard/
├── loaders/
│   └── trend_data_loader.py          ← Phase 1
├── analytics/
│   ├── audio_feature_engine.py       ← Phase 2
│   └── aggregation_engine.py          ← Phase 2
├── charts/
│   └── chart_render.py               ← Phase 2
└── validation/
```

Separation of concerns:
- **Loaders**: data access only (read-only, returns `df.copy()`)
- **Analytics**: aggregation only (no plotting, no file I/O)
- **Charts**: rendering only (Streamlit `st.*` calls, no business logic)

---

## 3. Audio Feature Display Registry

**File:** `analytics/audio_feature_engine.py`

12 audio features defined with display metadata:

| Feature | Display Name | Unit | Decimal |
|---|---|---|---|
| danceability | Danceability | — | 3 |
| energy | Energy | — | 3 |
| key | Musical Key | pitch class (0–11) | 0 |
| loudness | Loudness | dB | 2 |
| mode | Mode | binary (0=minor,1=major) | 0 |
| speechiness | Speechiness | — | 4 |
| acousticness | Acousticness | — | 3 |
| instrumentalness | Instrumentalness | — | 4 |
| liveness | Liveness | — | 3 |
| valence | Valence | — | 3 |
| tempo | Tempo | BPM | 2 |
| time_signature | Time Signature | beats/bar | 0 |

**Allow-list enforcement:** Only features in this registry can be selected in the UI. `is_valid_feature()` returns `False` for any unregistered name including `artist`, `genre`, `target_popularity`, `track_id`.

---

## 4. Aggregation Engine

**File:** `analytics/aggregation_engine.py`

| Function | Purpose |
|---|---|
| `filter_by_year(df, min, max)` | Returns copy of filtered DataFrame |
| `aggregate_popularity_by_year(df)` | Mean/median popularity per year |
| `aggregate_popularity_by_decade(df)` | Mean/median popularity per decade |
| `aggregate_audio_feature_by_year(df, feature)` | Mean/median single feature per year |
| `aggregate_audio_feature_by_decade(df, feature)` | Mean/median single feature per decade |

Each output dict includes:
- `data_points[]` with per-point coverage
- `overall_valid_rows`, `overall_total_rows`, `overall_coverage`
- `missing_years[]` (years in range but absent from data)
- `status`: `"OK"` or `"NO_DATA"`

---

## 5. Aggregation Contract

| Rule | Status |
|---|---|
| Mean and median supported | ✅ |
| Coverage reported per point and overall | ✅ |
| Never interpolate missing years | ✅ |
| Never fill missing values | ✅ |
| Never impute | ✅ |
| Never silent-drop to hide missingness | ✅ |

---

## 6. Popularity Trend Charts

### Chart: Average Popularity by Release Year
- **Type:** Bar chart
- **Aggregation:** `mean(target_popularity)` by `release_year`
- **Range:** 1922–2019
- **Year 1921:** NOT in dataset — no bar, no interpolation
- **Year 2020:** NOT in dataset — no bar, no interpolation

### Chart: Average Popularity by Decade
- **Type:** Bar chart
- **Aggregation:** `mean(target_popularity)` by decade
- **2020 edge case:** Labeled `2020 (single year)` — NOT `2020s`
- **Pre-computed `decade` column** used from source

### Chart: Track Count by Release Year
- **Type:** Bar chart
- **Aggregation:** Count of rows per year

---

## 7. Audio Feature Trend Charts

### Per-Feature Year Trend
- **Type:** Line chart (one feature at a time)
- **Feature selector:** Dropdown from allow-list (12 features)
- **No cross-feature overlay** on shared axes
- **No normalization** of different-units features

### Per-Feature Decade Trend
- **Type:** Bar chart
- **2020 edge case:** Labeled `2020 (single year)`

---

## 8. Empty / Insufficient Data States

| Scenario | Behavior |
|---|---|
| Filter produces 0 rows | Returns `status: NO_DATA`; chart not rendered |
| Only 1 year selected | Returns `status: OK` with 1 data point; no trend claim |
| All values null | Returns `status: NO_DATA`; no crash |

---

## 9. Key Field Name Corrections (Phase 1 → Phase 2)

| Field | WRONG name | CORRECT name | Unit |
|---|---|---|---|
| Popularity | `popularity` | `target_popularity` | 0–100 (int) |
| Duration | `duration_ms` | `duration_min` | **minutes** |
| Decade | (none) | `decade` column | pre-computed |

---

## 10. Chart Registry Summary

| Chart ID | Type | Granularity | Feature-Selectable |
|---|---|---|---|
| `popularity_year_trend` | bar | year | No |
| `popularity_decade_trend` | bar | decade | No |
| `audio_feature_year_trend` | line | year | Yes (12 features) |
| `audio_feature_decade_trend` | bar | decade | Yes (12 features) |
| `track_count_by_year` | bar | year | No |

---

## 11. Source Immutability

| Check | Status |
|---|---|
| Source dataset modified | NO ✅ |
| Analytics layer mutations | NONE ✅ |
| Model loaded | NO ✅ |
| Training executed | NO ✅ |
| SHAP computed | NO ✅ |

---

## 12. Warnings

| Warning | Severity |
|---|---|
| SHA-256 verification pending shell | LOW |
| Exact aggregate values pending pandas profiling | LOW |
| Integration with F3.3 page is Phase 3–4 | INFO |

---

## 13. Blockers

**None.**

---

## 14. Phase Gate

**Status: PASS WITH_WARNINGS — MAY BEGIN Phase 3**
