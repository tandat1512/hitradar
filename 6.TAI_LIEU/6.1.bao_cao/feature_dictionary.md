# FEATURE DICTIONARY — ML READY DATASET

**Source view:** `analytics.vw_ml_ready_dataset`  
**Rows:** 586,672  
**Columns:** 20  
**Feature:** 1.8 — ML-Safe Dataset Handoff  
**Owner:** Đạt

---

| column_name | role | dtype | description | allowed_range_or_values | null_handling_needed | use_for_training | notes |
|-------------|------|-------|-------------|-------------------------|----------------------|------------------|-------|
| track_id | identifier | text/varchar | Spotify track identifier for trace/debug | Non-null, unique | No | **No** | Identifier only — do NOT use as model input |
| target_popularity | label | integer | Spotify popularity score to predict (0–100) | 0–100 | No (0 nulls) | **No** (label) | Prediction target — NEVER use as input feature |
| duration_min | numeric_feature | double | Track duration in minutes | ~0.03–60+ min (short=26, long=83 outliers) | No | Yes | Scale in EPIC 2 |
| explicit | categorical_feature | boolean | Whether track is marked explicit | true / false | No | Yes | Encode boolean in EPIC 2 |
| release_year | time_sensitive_feature | integer | Year of release | observed range: 1921–2021 | No | Yes | Correlation +0.5909 with target — temporal split recommended |
| release_month | time_sensitive_feature | integer | Month of release (1–12) | 1–12 | **Yes — 136,489 NULL** | Yes | Time-sensitive; impute hoặc xử lý EPIC 2 |
| decade | time_sensitive_feature | integer | Decade bucket derived from release_year | e.g. 1990, 2000, 2010 | No | Yes | Time-sensitive feature |
| release_precision | categorical_feature | text/enum | Precision of release date (day/month/year) | day, month, year | No | Yes | Categorical — encode in EPIC 2 |
| danceability | numeric_feature | double | How suitable for dancing (Spotify audio feature) | 0.0–1.0 | No | Yes | Scale in EPIC 2 |
| energy | numeric_feature | double | Perceptual intensity and activity | 0.0–1.0 | No | Yes | Scale in EPIC 2 |
| key | numeric_feature | integer | Musical key (Pitch Class) | 0–11 | No | Yes | Ordinal/categorical encoding in EPIC 2 |
| loudness | numeric_feature | double | Overall loudness in dB | Typically −60 to 0 (219 rows > 0) | No | Yes | Scale in EPIC 2 |
| mode | numeric_feature | integer | Major (1) or minor (0) | 0 or 1 | No | Yes | Binary categorical |
| speechiness | numeric_feature | double | Presence of spoken words | 0.0–1.0 | No | Yes | Skew/zero-inflated — consider log-transform EPIC 2 |
| acousticness | numeric_feature | double | Confidence track is acoustic | 0.0–1.0 | No | Yes | Scale in EPIC 2 |
| instrumentalness | numeric_feature | double | Likelihood track has no vocals | 0.0–1.0 | No | Yes | Skew/zero-inflated — consider log-transform EPIC 2 |
| liveness | numeric_feature | double | Presence of audience in recording | 0.0–1.0 | No | Yes | Scale in EPIC 2 |
| valence | numeric_feature | double | Musical positiveness | 0.0–1.0 | No | Yes | Scale in EPIC 2 |
| tempo | numeric_feature | double | Estimated BPM | ~50–250 typical | **Yes — 328 NULL** | Yes | Impute with median in EPIC 2 (fit on train only) |
| time_signature | numeric_feature | integer | Estimated time signature | 3, 4, 5, etc. | **Yes — 337 NULL** | Yes | Impute with mode in EPIC 2 (fit on train only) |

---

## Role Summary

| Role | Columns |
|------|---------|
| identifier | track_id |
| label | target_popularity |
| numeric_feature | duration_min, release_year, release_month, decade, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature |
| categorical_feature | explicit, release_precision |
| time_sensitive_feature | release_year, release_month, decade |
| non_training | track_id, target_popularity |

---

## EPIC 2 Preprocessing Notes (not done in EPIC 1)

- **Impute:** tempo (median), time_signature (mode) — fit imputer on train split only
- **Scale:** all numeric features — fit scaler on train split only
- **Encode:** explicit (boolean), release_precision (categorical)
- **Transform:** log-transform speechiness, instrumentalness (skew/zero-inflated)
- **Split:** prefer temporal split by release_year (time bias risk)
- **Genre:** 4,672 track-linked genres exist in source data but NOT in this baseline view — if added in EPIC 2, use top-N / target encoding on train only

---

*Feature 1.8 — ML-Safe Dataset Handoff | HitRadar Pro*
