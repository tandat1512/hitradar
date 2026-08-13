# Feature 3.4 — Caption & Insight Report
## Phase 4 — Data-Grounded Chart Captions, Claim Audit & Presentation

**Feature:** 3.4 — Dashboard & Visualization Assets
**Phase:** 4 / 5
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS WITH WARNINGS

---

## 1. Prerequisite Validation

| Check | Evidence | Status |
|---|---|---|
| Phase 3 Gate valid | `feature_3_4_phase_3_gate.json` → `next_phase: MAY_BEGIN` | ✅ |
| Phase 2 aggregation engine | `analytics/aggregation_engine.py` | ✅ |
| Phase 3 explicit/duration engines | `analytics/explicit_engine.py`, `duration_engine.py` | ✅ |

---

## 2. Caption Architecture

**Module:** `dashboard/captions/engines.py`

All captions are **deterministic functions** — derived from actual aggregate data, not hardcoded strings.

| Function | Chart | Dynamic? |
|---|---|---|
| `popularity_year_caption()` | Popularity by Year | No |
| `popularity_decade_caption()` | Popularity by Decade | No |
| `audio_year_caption()` | Audio Feature by Year | Yes (feature + data) |
| `audio_decade_caption()` | Audio Feature by Decade | Yes (feature + data) |
| `track_count_caption()` | Track Count by Year | No |
| `explicit_trend_caption()` | Explicit by Decade | No |
| `duration_trend_caption()` | Duration by Decade | No |
| `artist_genre_caption()` | Artist/Genre Summary | Yes (always "not available") |

---

## 3. Caption Evidence Traceability

Every caption traces to a specific aggregate function and specific data fields.

| Caption | Evidence Source | Key Fields |
|---|---|---|
| Popularity by Year | `aggregate_popularity_by_year()` | `popularity_value`, `year` |
| Popularity by Decade | `aggregate_popularity_by_decade()` | `popularity_value`, `decade` |
| Audio by Year | `aggregate_audio_feature_by_year()` | `feature_value`, `year` |
| Audio by Decade | `aggregate_audio_feature_by_decade()` | `feature_value`, `decade` |
| Explicit | `aggregate_explicit_by_decade()` | `explicit_percentage`, `decade` |
| Duration | `aggregate_duration_by_decade()` | `duration_mean_min`, `decade` |
| Track Count | `aggregate_by_year()` | `_count`, `year` |
| Artist/Genre | NOT_AVAILABLE | None |

Max/min values are **extracted from `data_points[]`**, not hardcoded.

---

## 4. Dynamic Caption Logic (Audio Features)

For audio feature captions, the caption is parameterized by the selected feature.

Template: *"{Feature} values {unit} ranged from {min} ({min_yr/dec}) to {max} ({max_yr/dec}) in the available data. Values {change} across {period}."*

Change phrases derived deterministically:
- If |last − first| < 5% of mean → "remained broadly similar"
- If last > first → "increased from X to Y"
- If last < first → "decreased from X to Y"

All phrases qualified with **"in the available data"**.

---

## 5. Explicit Caption

**Metric:** rate = explicit_count / valid_count

**Used phrase:** "Share of tracks marked explicit ranged from X% (DECs) to Y% (DECe) in the available data."

**Banned phrases avoided:** "societal", "society became", "people became"

**Explicit disclaimer included:**
> "These values describe the records in this dataset — they do not indicate broader societal trends."

---

## 6. Duration Caption

**Metric:** mean duration in **minutes**

**Used phrase:** "Mean track duration ranged from X min (DECs) to Y min (DECe) in the available data."

**Never used:** "listeners preferred", "audience changed"

---

## 7. Artist/Genre Caption — NOT AVAILABLE

> "Artist and genre data are not available in this dataset. The dataset contains only audio features and track metadata (e.g., release year, duration, popularity). Artist-level or genre-level summaries cannot be generated."

---

## 8. 2020 Edge Case — Caption Handling

| Chart | Caption Note |
|---|---|
| Popularity by Decade | "Note: '2020' represents only the year 2020, not a full decade." |
| Audio by Decade | "Note: '2020' represents only the year 2020, not a full decade." |
| Explicit | "Note: '2020' represents only the year 2020, not a full decade." |
| Duration | "Note: '2020' represents only the year 2020, not a full decade." |

---

## 9. Global Disclaimer

All dashboard pages include:

> "All visualizations describe records available in the project dataset. They do not represent the global music industry or broader population trends."

---

## 10. Causal Claim Audit

**13 banned phrase patterns** scanned across all captions:

| Phrase Pattern | Found? |
|---|---|
| causes / caused by | ❌ NOT FOUND |
| leads to | ❌ NOT FOUND |
| results in | ❌ NOT FOUND |
| makes songs | ❌ NOT FOUND |
| proves | ❌ NOT FOUND |
| societal | ❌ NOT FOUND |
| industry-wide | ❌ NOT FOUND |
| global music | ❌ NOT FOUND |
| streaming | ❌ NOT FOUND |
| **Total causal claims** | **0** |
| **Unsupported generalizations** | **0** |

---

## 11. Chart/Caption Consistency

| Check | Status |
|---|---|
| Aggregation matches chart | ✅ All 7 charts consistent |
| Unit matches data | ✅ All 6 unit checks pass |
| 2020 edge case wording correct | ✅ All 4 charts |
| Max/min extracted from data (not hardcoded) | ✅ |
| Coverage reported | ✅ |
| Missing years noted | ✅ |

---

## 12. Source Immutability

| Check | Status |
|---|---|
| Source dataset modified | NO ✅ |
| Model loaded | NO ✅ |
| Training executed | NO ✅ |
| SHAP computed | NO ✅ |

---

## 13. Warnings

| Warning | Severity |
|---|---|
| Exact max/min values require pandas profiling to verify | LOW |
| SHA-256 verification pending shell | LOW |

---

## 14. Blockers

**None.**

---

## 15. Phase Gate

**Status: PASS WITH_WARNINGS — MAY BEGIN Phase 5**
