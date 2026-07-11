# HANDOFF TO EPIC 2 — ML-SAFE DATASET

**Feature:** 1.8 — ML-Safe Dataset Handoff  
**From:** EPIC 1 — Data Foundation & Data Understanding  
**To:** EPIC 2 — ML Modeling  
**Owner:** Đạt  
**Date:** 2026-07-11

---

## 1. Dataset

| Property | Value |
|----------|-------|
| Source view | `analytics.vw_ml_ready_dataset` |
| Upstream source | `analytics.vw_ml_training_dataset` |
| Rows | 586,672 |
| Columns | 20 |
| SQL script | `2.DATABASE_SQL/2.6.ml_handoff/01_create_ml_ready_dataset.sql` |

### Export Files

| Format | Path | Notes |
|--------|------|-------|
| CSV | `5.DATA/processed/ml_ready_dataset.csv` | Required |
| Parquet | `5.DATA/processed/ml_ready_dataset.parquet` | If pyarrow/fastparquet available |

### Export / Validate Scripts

- `9.SCRIPTS/export_ml_ready_dataset.py`
- `9.SCRIPTS/validate_ml_ready_dataset.py`

---

## 2. Label

| Column | Type | Range | Notes |
|--------|------|-------|-------|
| `target_popularity` | integer | 0–100 | Spotify popularity — **label only**, never input |

---

## 3. Allowed Baseline Input Features (18)

```
duration_min
explicit
release_year
release_month
decade
release_precision
danceability
energy
key
loudness
mode
speechiness
acousticness
instrumentalness
liveness
valence
tempo
time_signature
```

### Notes

| Feature | Type | Note |
|---------|------|------|
| release_year, release_month, decade | time-sensitive | Correlation +0.5909 (release_year vs target) — prefer temporal split |
| release_precision | categorical | Values: day, month, year — encode in EPIC 2 |
| explicit | boolean | Encode in EPIC 2 |
| tempo, time_signature | numeric | Have NULLs — impute in EPIC 2 (train-only fit) |
| speechiness, instrumentalness | numeric | Skew/zero-inflated — consider log-transform |

---

## 4. Non-Training Columns

| Column | Role |
|--------|------|
| track_id | Identifier — trace/debug only |
| target_popularity | Label — prediction target |

---

## 5. Explicitly Excluded Leakage Features

**Not present in handoff view — do NOT add without leakage review:**

- `artists.popularity`
- `artist_popularity_dashboard_only`
- `avg_artist_popularity`, `avg_genre_popularity`, `avg_track_popularity`
- `popularity_bucket`, `popularity_group` (derived from target)
- `train_split`, `test_split`, `split`
- `imputed_*`, `scaled_*`, `label_encoded`
- `future_popularity`
- Any post-split global statistics

See: `ml_excluded_columns.md`, `data_leakage_risks.md`

---

## 6. Data Quality Warnings (Carry-Forward)

| Issue | Count / Detail | Severity |
|-------|----------------|----------|
| Duration very short | 26 tracks | Warning |
| Duration very long | 83 tracks | Warning |
| loudness > 0 | 219 tracks | Warning |
| tempo NULL | 328 | Warning — impute EPIC 2 |
| time_signature NULL | 337 | Warning — impute EPIC 2 |
| release_month NULL | 136,489 | Warning — impute hoặc xử lý EPIC 2 |
| target_popularity = 0 | 44,690 (~7.6%) | Warning |
| Popularity imbalance | ~75% tracks ≤ 40 | Warning |
| track_artists coverage | 96.54% | Warning |

---

## 7. Recommended EPIC 2 Preprocessing

1. **Split:** Temporal split by `release_year` (preferred over random).
2. **Impute:** tempo → median; time_signature → mode; release_month → mode hoặc strategy riêng (fit on train only).
3. **Encode:** `release_precision` (categorical); `explicit` (boolean).
4. **Scale:** Numeric features (fit scaler on train only).
5. **Transform:** Log-transform `speechiness`, `instrumentalness` (skew).
6. **Genre (optional):** 4,672 track-linked genres in source — do NOT one-hot all by default.
   - Use top-N, limited multi-hot, target encoding (train-only fit), or embedding.
7. **Pipeline order:** Split → fit preprocessors on train → transform train & test.

---

## 8. EPIC 2 Risks

| Risk | Mitigation |
|------|------------|
| Time bias | Temporal split; error analysis by decade |
| Popularity imbalance | Weighted metrics; stratified sampling |
| Leakage via popularity proxy | Do not add artist/genre popularity by default |
| Long-tail genre/artist | Top-N or embedding; not full one-hot |
| Popularity ≠ musical quality | Clear model card limitations |

---

## 9. Handoff Decision

| Criterion | Status |
|-----------|--------|
| View `analytics.vw_ml_ready_dataset` exists | ✅ Yes |
| Row count = 586,672 | ✅ Yes |
| 20 required columns | ✅ Yes |
| No leakage columns | ✅ Yes |
| CSV export exists | ✅ Yes (69.19 MB) |
| Parquet export | ✅ Yes (25.22 MB) |
| Documentation complete | ✅ Yes |
| Validation script executed | ✅ Yes — PASS_WITH_WARNINGS |

**Final decision:** **PASS_WITH_WARNINGS**

Dataset is ready for EPIC 2. Carry-forward warnings: tempo/time_signature/release_month NULLs, popularity imbalance.

---

## Reference Documents

| Document | Path |
|----------|------|
| Feature dictionary | `6.TAI_LIEU/6.1.bao_cao/feature_dictionary.md` |
| Excluded columns | `6.TAI_LIEU/6.1.bao_cao/ml_excluded_columns.md` |
| Leakage risks | `6.TAI_LIEU/6.1.bao_cao/data_leakage_risks.md` |
| Popularity limitations | `6.TAI_LIEU/6.1.bao_cao/popularity_limitations.md` |
| Validation report | `6.TAI_LIEU/6.1.bao_cao/ML_READY_DATASET_VALIDATION_REPORT.md` |
| EDA insights | `6.TAI_LIEU/6.1.bao_cao/EDA_INSIGHTS_REPORT.md` |

---

*Feature 1.8 — ML-Safe Dataset Handoff | HitRadar Pro*
