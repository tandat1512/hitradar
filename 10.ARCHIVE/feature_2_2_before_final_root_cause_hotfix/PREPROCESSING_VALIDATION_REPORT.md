# PREPROCESSING VALIDATION REPORT

**Feature 2.2 — Leakage-Safe Preprocessing Pipeline**
**HitRadar Pro — EPIC 2**

**Repository URL**: https://github.com/tandat1512/hitradar.git
**Source Branch**: main
**Source Commit Used for Generation**: 1352fc050d73796e67620d5fd63d44661f2172f2
**Source Commit Timestamp**: 2026-07-18 14:29:58 +0700
**Working Tree Status**: DIRTY
**Generator Path**: 9.SCRIPTS/feature_2_2_preprocessing.py
**Generator SHA-256**: 2bf4f510d987b65b5b0206376a651f43dfa64ab97996973dba0447c740181fdf
**Generated Timestamp**: 2026-07-18T10:33:13.118872+00:00
**Data Version**: ml-ready-2026-07-17-v1
**Split Version**: temporal-split-v1
**Test Summary Path**: 7.ML/7.5.preprocessing/feature_2_2_test_summary.json
**JUnit XML Path**: 7.ML/7.5.preprocessing/pytest_feature_2_2.xml
**Report Manifest Path**: 7.ML/7.5.preprocessing/feature_2_2_report_manifest.json
**Closure Gate Path**: 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json

---

## 1. Kết luận điều hành
61 checks kỹ thuật đã được chạy, 100% Pass.

## 2. Technical Evidence
| Check ID | Expected | Actual | Evidence Path | Pointer | Status |
|---|---|---|---|---|---|
| INPUT-ROWS | 586672 | 586672 | 5.DATA/processed/ml_ready_dataset.parquet | df.shape[0] | PASS |
| INPUT-COLUMNS | 20 | 20 | 5.DATA/processed/ml_ready_dataset.parquet | df.shape[1] | PASS |
| INPUT-IDENTIFIER | track_id | track_id | 5.DATA/processed/ml_ready_dataset.parquet | df.columns | PASS |
| INPUT-TARGET | target_popularity | target_popularity | 5.DATA/processed/ml_ready_dataset.parquet | df.columns | PASS |
| INPUT-TRAIN_ROWS | 415524 | 415524 | 7.ML/7.4.splits/train_ids.parquet | len(train_ids) | PASS |
| SEMANTIC-18-FEATURES | 18 | 18 | 5.DATA/processed/ml_ready_dataset.parquet | input_feature_count | PASS |
| IMPUTE-TEMPO-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/imputer_statistics.json | fitted_on_split | PASS |
| IMPUTE-TIME_SIGNATURE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/imputer_statistics.json | fitted_on_split | PASS |
| OUTLIER-DURATION_MIN-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | fitted_on_split | PASS |
| OUTLIER-TEMPO-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | fitted_on_split | PASS |
| OUTLIER-LOUDNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | fitted_on_split | PASS |
| ENCODE-P22-A-RELEASE_MONTH-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-DECADE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-RELEASE_PRECISION-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-KEY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-TIME_SIGNATURE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-RELEASE_MONTH-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-DECADE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-RELEASE_PRECISION-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-KEY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-TIME_SIGNATURE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-RELEASE_MONTH-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-DECADE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-RELEASE_PRECISION-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-KEY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-TIME_SIGNATURE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-RELEASE_MONTH-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-DECADE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-RELEASE_PRECISION-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-KEY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-TIME_SIGNATURE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| SCALE-P22-A-DURATION_MIN-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-RELEASE_YEAR-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-DANCEABILITY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-ENERGY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-LOUDNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-SPEECHINESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-ACOUSTICNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-INSTRUMENTALNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-LIVENESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-VALENCE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-TEMPO-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-DURATION_MIN-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-RELEASE_YEAR-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-DANCEABILITY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-ENERGY-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-LOUDNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-SPEECHINESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-ACOUSTICNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-INSTRUMENTALNESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-LIVENESS-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-VALENCE-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-TEMPO-TRAIN-ONLY | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCHEMA-P22-A-NO-NAN | False | False | 7.ML/7.5.preprocessing/p22_a/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-A-NO-INF | False | False | 7.ML/7.5.preprocessing/p22_a/output_schema.json | contains_inf | PASS |
| SCHEMA-P22-B-NO-NAN | False | False | 7.ML/7.5.preprocessing/p22_b/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-B-NO-INF | False | False | 7.ML/7.5.preprocessing/p22_b/output_schema.json | contains_inf | PASS |
| SCHEMA-P22-C-NO-NAN | False | False | 7.ML/7.5.preprocessing/p22_c/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-C-NO-INF | False | False | 7.ML/7.5.preprocessing/p22_c/output_schema.json | contains_inf | PASS |
| SCHEMA-P22-D-NO-NAN | False | False | 7.ML/7.5.preprocessing/p22_d/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-D-NO-INF | False | False | 7.ML/7.5.preprocessing/p22_d/output_schema.json | contains_inf | PASS |
