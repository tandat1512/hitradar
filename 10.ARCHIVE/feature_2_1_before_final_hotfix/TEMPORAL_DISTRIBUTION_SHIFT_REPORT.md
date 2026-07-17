# TEMPORAL DISTRIBUTION SHIFT REPORT

**Feature 2.1 HOTFIX — HitRadar Pro EPIC 2**

---

## 1. Summary

Temporal split by `release_year` creates **severe distribution shift** between train and validation/test. This is NOT an "expected warning" — it is a **HIGH severity risk** that must be addressed in Feature 2.5 evaluation.

---

## 2. Target Distribution Shift

| Metric | Train (1900–2004) | Validation (2005–2013) | Test (2014–2021) |
|---|---:|---:|---:|
| Rows | 415,524 | 85,272 | 85,876 |
| Target mean | 22.88 | 37.06 | 40.84 |
| Target median | 22.0 | 39.0 | 45.0 |
| Target std | 19.28 | 22.66 | 24.73 |
| Target zero count | 35,952 | 3,144 | 5,594 |

### Target Mean Shift

| Comparison | Delta | Severity |
|---|---:|---|
| Train → Validation | **+14.18** | **HIGH** |
| Train → Test | **+17.96** | **HIGH** |

### Population Stability Index (PSI)

| Comparison | PSI | Interpretation |
|---|---:|---|
| Train vs Validation | **0.8709** | **Highly significant** (>> 0.25) |
| Train vs Test | **1.5385** | **Highly significant** (>> 0.25) |

PSI thresholds: < 0.1 insignificant, 0.1–0.25 moderate, > 0.25 significant.

---

## 3. Feature Distribution Shift (KS Test)

Only features with KS statistic > 0.1 (significant) are listed:

| Feature | Train vs Val KS | Train vs Test KS | Severity |
|---|---:|---:|---|
| **loudness** | **0.4261** | **0.4240** | **HIGH** |
| **acousticness** | **0.2692** | **0.3017** | **HIGH** |
| **energy** | **0.2952** | **0.2927** | **HIGH** |
| danceability | 0.1090 | 0.2009 | MEDIUM–HIGH |
| duration_min | 0.1811 | — | MEDIUM |
| speechiness | — | 0.1708 | MEDIUM |
| instrumentalness | 0.1563 | 0.1564 | MEDIUM |
| valence | — | 0.1156 | MEDIUM |
| tempo | 0.1124 | 0.1142 | MEDIUM |

All p-values ≈ 0 (highly significant). These shifts reflect genuine temporal evolution in music production, not data errors.

---

## 4. Missing Value Distribution Shift

| Feature | Train NULL ratio | Val NULL ratio | Test NULL ratio | Severity |
|---|---:|---:|---:|---|
| **release_month** | **0.3054** | **0.0992** | **0.0133** | **HIGH** |
| tempo | 0.0008 | 0.0000 | 0.0000 | LOW |
| time_signature | 0.0008 | 0.0000 | 0.0000 | LOW |

`release_month` missing rate drops from 30.5% (train) to 1.3% (test). This is expected — older Spotify catalog records have less complete metadata — but creates a strong temporal proxy risk (see TEMPORAL_PROXY_RISK_REPORT.md).

---

## 5. Risk Classification

| Risk ID | Description | Severity | Owner |
|---|---|---|---|
| SHIFT-01 | Target mean shift +17.96 (train→test) | **HIGH** | Feature 2.5 |
| SHIFT-02 | PSI > 1.5 for target distribution | **HIGH** | Feature 2.5 |
| SHIFT-03 | loudness KS > 0.42 | **HIGH** | Feature 2.2/2.5 |
| SHIFT-04 | acousticness KS > 0.30 | **HIGH** | Feature 2.2/2.5 |
| SHIFT-05 | energy KS > 0.29 | **HIGH** | Feature 2.2/2.5 |
| SHIFT-06 | release_month NULL ratio shift 0.305→0.013 | **HIGH** | Feature 2.2 |
| SHIFT-07 | danceability/speechiness/tempo KS > 0.10 | MEDIUM | Feature 2.5 |

---

## 6. Implications for EPIC 2

1. **Feature 2.2 (Preprocessing)**: Missing value imputation for `release_month` must use train-only statistics. The imputer will see 30.5% NULLs in train but only 1.3% in test — this asymmetry is unavoidable with temporal split.

2. **Feature 2.3 (Feature Engineering)**: Features derived from audio characteristics (loudness, acousticness, energy) will have different distributions. Feature selection metrics computed on train may not generalize.

3. **Feature 2.5 (Evaluation)**: Model performance on test will likely be worse than on validation for a train-fitted model, because the test distribution is even further from train. Per-decade and per-bucket evaluation is MANDATORY, not optional.

4. **Baseline expectation**: A simple mean predictor trained on train (mean ≈ 22.88) would have MAE ≈ 18 on test (mean ≈ 40.84). Any useful model must significantly beat this.

---

## 7. What This Report Does NOT Do

- Does NOT recommend changing split boundaries
- Does NOT recommend using random split instead
- Does NOT use test set for model selection
- All statistics are for risk documentation only

---

## 8. Evidence Files

| File | Purpose |
|---|---|
| `7.ML/7.3.data_intake/temporal_shift_profile.json` | PSI, KS statistics, feature profiles |
| `7.ML/7.3.data_intake/split_candidate_diagnostics.csv` | Per-candidate statistics |
