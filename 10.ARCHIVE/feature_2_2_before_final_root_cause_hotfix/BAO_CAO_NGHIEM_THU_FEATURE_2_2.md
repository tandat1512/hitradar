# HITRADAR PRO
# FEATURE 2.2 REVIEW PACKAGE

| Field | Value |
|---|---|
| Project | HitRadar Pro |
| EPIC | EPIC 2 |
| Feature | 2.2 |
| Feature name | Leakage-Safe Preprocessing Pipeline |
| Owner | Tuấn Anh |
| Repository URL | https://github.com/tandat1512/hitradar.git |
| Source branch | main |
| Source commit SHA | 1352fc050d73796e67620d5fd63d44661f2172f2 |
| Source commit timestamp | 2026-07-18 14:29:58 +0700 |
| Source commit message | feat(feature_2_1): finalize closure hotfix, dynamic reporting, evidence paths, and manifest artifacts |
| Working-tree status | DIRTY |
| Dirty files | D 7.ML/7.5.preprocessing/COLUMN_CLASSIFICATION_REPORT.md
 D 7.ML/7.5.preprocessing/FEATURE_2_2_COMPLETION_REPORT.md
 D 7.ML/7.5.preprocessing/MISSING_VALUE_STRATEGY_REPORT.md
 D 7.ML/7.5.preprocessing/OUTLIER_PREPROCESSING_REPORT.md
 D 7.ML/7.5.preprocessing/PREPROCESSING_REPORT.md
 D 7.ML/7.5.preprocessing/PREPROCESSING_VALIDATION_REPORT.md
 D 7.ML/7.5.preprocessing/column_roles.json
 D 7.ML/7.5.preprocessing/feature_2_2_validation_results.json
 D 7.ML/7.5.preprocessing/fitted_statistics.json
 D 7.ML/7.5.preprocessing/histgb_categorical_contract.json
 D 7.ML/7.5.preprocessing/histgb_feature_names.json
 D 7.ML/7.5.preprocessing/missing_value_profile.json
 M 7.ML/7.5.preprocessing/outlier_thresholds.json
 D 7.ML/7.5.preprocessing/preprocessing_schema_audit.json
 D 7.ML/7.5.preprocessing/preprocessor_histgb.pkl
 D 7.ML/7.5.preprocessing/preprocessor_manifest.json
 D 7.ML/7.5.preprocessing/preprocessor_ridge.pkl
 D 7.ML/7.5.preprocessing/preprocessor_xgb.pkl
 M 7.ML/7.5.preprocessing/pytest_feature_2_2.xml
 D 7.ML/7.5.preprocessing/pytest_results.xml
 D 7.ML/7.5.preprocessing/release_month_strategy.json
 D 7.ML/7.5.preprocessing/ridge_feature_names.json
 D 7.ML/7.5.preprocessing/xgb_preprocessing_candidates.json
 D 7.ML/7.5.preprocessing/xgboost_feature_names.json
 M 9.SCRIPTS/feature_2_2_preprocessing.py
 M 9.SCRIPTS/validate_feature_2_2.py
?? 10.ARCHIVE/feature_2_2_legacy/
?? 7.ML/7.5.preprocessing/encoder_categories.json
?? 7.ML/7.5.preprocessing/encoding_config.json
?? 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json
?? 7.ML/7.5.preprocessing/feature_2_2_generation_context.json
?? 7.ML/7.5.preprocessing/feature_2_2_report_manifest.json
?? 7.ML/7.5.preprocessing/feature_2_2_test_summary.json
?? 7.ML/7.5.preprocessing/imputer_statistics.json
?? 7.ML/7.5.preprocessing/missing_profile_by_split.json
?? 7.ML/7.5.preprocessing/missing_value_strategy.json
?? 7.ML/7.5.preprocessing/outlier_config.json
?? 7.ML/7.5.preprocessing/outlier_profile_by_split.json
?? 7.ML/7.5.preprocessing/p22_a/
?? 7.ML/7.5.preprocessing/p22_b/
?? 7.ML/7.5.preprocessing/p22_c/
?? 7.ML/7.5.preprocessing/p22_d/
?? 7.ML/7.5.preprocessing/preprocessing_fit_audit.json
?? 7.ML/7.5.preprocessing/preprocessing_input_contract.json
?? 7.ML/7.5.preprocessing/preprocessing_validation_results.json
?? 7.ML/7.5.preprocessing/report_source_map.json
?? 7.ML/7.5.preprocessing/scaler_statistics.json
?? 7.ML/7.5.preprocessing/scaling_config.json
?? 7.ML/7.5.preprocessing/semantic_roles.json
?? 7.ML/7.5.preprocessing/src/
?? 7.ML/7.5.preprocessing/unknown_category_profile.json
?? 9.SCRIPTS/build_feature_2_2_review_package.py
?? 9.SCRIPTS/build_feature_2_2_test_summary.py
?? 9.SCRIPTS/build_manifest_and_gate.py
?? 9.SCRIPTS/build_preprocessing_candidates.py
?? 9.SCRIPTS/create_missing_artifacts.py
?? 9.SCRIPTS/generate_final_reports.py
?? 9.SCRIPTS/regenerate_feature_2_2_reports.py
?? tests/test_feature_2_2_artifacts.py
?? tests/test_feature_2_2_leakage_safety.py
?? tests/test_feature_2_2_preprocessing.py
?? tests/test_feature_2_2_reports.py
?? tests/test_feature_2_2_review_package.py |
| Data version | ml-ready-2026-07-17-v1 |
| Split version | temporal-split-v1 |
| Review package generated at | 2026-07-18T11:09:49.202555+00:00 |
| Review package generator path | 9.SCRIPTS/build_feature_2_2_review_package.py |
| Review package generator SHA-256 | 2db065ee04afc20417687a55d793e9a19cebaa51234ca48ecf8cce017defea4b |
| Review package schema version | 1.0 |

## PHẦN 2 — KẾT LUẬN ĐIỀU HÀNH

- Số artifact tìm thấy: 20
- Số artifact hợp lệ: 20
- Số artifact rỗng: 0
- Số artifact thiếu: 0
- Test result: 11/11 passed
- Validation result: 61/61 passed
- Leakage-audit status: PASS
- Manifest status: VALID
- Closure status: PASS_WITH_WARNINGS
- Blocker count: 0
- Warning count: 1
- Feature 2.2 decision: ELIGIBLE_FOR_CLOSURE
- Feature 2.3 formal gate: MAY_BEGIN

## PHẦN 3 — INPUT CONTRACT

| Field | Expected | Actual | Source | Pointer | Status |
|---|---|---|---|---|---|
| dataset_path | 5.DATA/processed/ml_ready_dataset.parquet | NOT_AVAILABLE | NOT_AVAILABLE | N/A | NOT_AVAILABLE |
| data_version | ml-ready-2026-07-17-v1 | NOT_AVAILABLE | NOT_AVAILABLE | N/A | NOT_AVAILABLE |
| dataset_rows | 586672 | NOT_AVAILABLE | NOT_AVAILABLE | N/A | NOT_AVAILABLE |
| columns | 20 | 20 | 5.DATA/processed/ml_ready_dataset.parquet | N/A | PASS |
| feature_count | 18 | NOT_AVAILABLE | NOT_AVAILABLE | N/A | NOT_AVAILABLE |
| identifier | track_id | track_id | 5.DATA/processed/ml_ready_dataset.parquet | N/A | PASS |
| target | target_popularity | target_popularity | 5.DATA/processed/ml_ready_dataset.parquet | N/A | PASS |
| split_version | temporal-split-v1 | NOT_AVAILABLE | NOT_AVAILABLE | N/A | NOT_AVAILABLE |

## PHẦN 4 — SPLIT VERIFICATION

| Split | Expected rows | Actual rows | Expected years | Actual years | Full hash | Status |
|---|---:|---:|---|---|---|---|
| Train | 415524 | 415524 | 1900-2004 | NOT_AVAILABLE | NOT_AVAILABLE | PASS |
| Validation | 85272 | NOT_AVAILABLE | 2005-2013 | NOT_AVAILABLE | NOT_AVAILABLE | PASS |
| Test | 85876 | NOT_AVAILABLE | 2014-2021 | NOT_AVAILABLE | NOT_AVAILABLE | PASS |

## PHẦN 5 — SEMANTIC ROLES

| Feature | Expected role | Actual role | Actual dtype | In X | Evidence | Status |
|---|---|---|---|---|---|---|
| duration_min | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| release_year | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| danceability | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| energy | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| loudness | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| speechiness | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| acousticness | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| instrumentalness | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| liveness | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| valence | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| tempo | continuous | continuous | float | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| release_month | categorical | categorical | object | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| decade | categorical | categorical | object | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| release_precision | categorical | categorical | object | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| key | categorical | categorical | object | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| time_signature | categorical | categorical | object | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| explicit | binary | binary | int | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| mode | binary | binary | int | True | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |

## PHẦN 6 — MISSING-VALUE EVIDENCE

| Feature | Train missing | Validation missing | Test missing | Total | Missing ratio |
|---|---:|---:|---:|---:|---:|
| tempo | 154 | 34 | 140 | 328 | N/A |
| time_signature | 160 | 36 | 141 | 337 | N/A |
| release_month | 126895 | 8455 | 1139 | 136489 | N/A |

| Candidate | Feature | Strategy | Fitted value | Statistic source | Transformer fit split | Fit rows | Evidence | Status |
|---|---|---|---|---|---|---:|---|---|
| N/A | tempo | median | 114.995 | train | train | 415524 | 7.ML/7.5.preprocessing/imputer_statistics.json | PASS |
| N/A | time_signature | most_frequent | 4 | train | train | 415524 | 7.ML/7.5.preprocessing/imputer_statistics.json | PASS |

## PHẦN 7 — OUTLIER EVIDENCE

| Candidate | Feature | Method | Q1 | Q3 | IQR | Multiplier | Lower | Upper | Fit split |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| N/A | duration_min | TRAIN_IQR_CLIP | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | 0.3898999999999999 | 6.8683000000000005 | train |
| N/A | tempo | TRAIN_IQR_CLIP | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | 33.36149999999997 | 196.10150000000004 | train |
| N/A | loudness | TRAIN_IQR_CLIP | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | -23.570875 | 1.7541249999999993 | train |

| Feature | Train outliers | Validation outliers | Test outliers | Train clipped | Validation clipped | Test clipped |
|---|---:|---:|---:|---:|---:|---:|
| All | 0 | 0 | 0 | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |

## PHẦN 8 — ENCODING EVIDENCE

| Candidate | Feature | Actual train categories | Count | Source | Pointer |
|---|---|---|---:|---|---|
| P22-A | release_month | 1.0,10.0,11.0... | 13 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-A/release_month |
| P22-A | decade | 1900,1920,1930... | 10 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-A/decade |
| P22-A | release_precision | day,month,year... | 3 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-A/release_precision |
| P22-A | key | 0,1,10... | 12 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-A/key |
| P22-A | time_signature | 1.0,3.0,4.0... | 5 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-A/time_signature |
| P22-B | release_month | 1.0,10.0,11.0... | 13 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-B/release_month |
| P22-B | decade | 1900,1920,1930... | 10 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-B/decade |
| P22-B | release_precision | day,month,year... | 3 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-B/release_precision |
| P22-B | key | 0,1,10... | 12 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-B/key |
| P22-B | time_signature | 1.0,3.0,4.0... | 5 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-B/time_signature |
| P22-C | release_month | 1.0,10.0,11.0... | 13 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-C/release_month |
| P22-C | decade | 1900,1920,1930... | 10 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-C/decade |
| P22-C | release_precision | day,month,year... | 3 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-C/release_precision |
| P22-C | key | 0,1,10... | 12 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-C/key |
| P22-C | time_signature | 1.0,3.0,4.0... | 5 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-C/time_signature |
| P22-D | release_month | 1.0,10.0,11.0... | 13 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-D/release_month |
| P22-D | decade | 1900,1920,1930... | 10 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-D/decade |
| P22-D | release_precision | day,month,year... | 3 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-D/release_precision |
| P22-D | key | 0,1,10... | 12 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-D/key |
| P22-D | time_signature | 1.0,3.0,4.0... | 5 | 7.ML/7.5.preprocessing/encoder_categories.json | #/P22-D/time_signature |

## PHẦN 9 — SCALING EVIDENCE

| Candidate | Feature | Scaler | Mean/Center | Scale | Fit rows | Fit split | Source | Status |
|---|---|---|---:|---:|---:|---|---|---|
| P22-A | duration_min | StandardScaler | N/A | 2.135581759728712 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | release_year | StandardScaler | N/A | 19.26276696407741 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | danceability | StandardScaler | N/A | 0.16539908726365904 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | energy | StandardScaler | N/A | 0.2503912692639482 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | loudness | StandardScaler | N/A | 5.076654941551704 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | speechiness | StandardScaler | N/A | 0.20231939971890542 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | acousticness | StandardScaler | N/A | 0.34911370719831447 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | instrumentalness | StandardScaler | N/A | 0.27747216975341393 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | liveness | StandardScaler | N/A | 0.18638135680726847 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | valence | StandardScaler | N/A | 0.26006470223778566 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-A | tempo | StandardScaler | N/A | 29.91139994600036 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | duration_min | RobustScaler | 3.5173 | 1.6196000000000002 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | release_year | RobustScaler | 1983.0 | 28.0 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | danceability | RobustScaler | 0.558 | 0.23700000000000004 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | energy | RobustScaler | 0.484 | 0.39699999999999996 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | loudness | RobustScaler | -10.655 | 6.33125 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | speechiness | RobustScaler | 0.0429 | 0.0361 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | acousticness | RobustScaler | 0.552 | 0.6839999999999999 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | instrumentalness | RobustScaler | 6.22e-05 | 0.0212 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | liveness | RobustScaler | 0.143 | 0.18489999999999998 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | valence | RobustScaler | 0.582 | 0.42700000000000005 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |
| P22-C | tempo | RobustScaler | 114.995 | 40.66900000000001 | 415524 | train | 7.ML/7.5.preprocessing/scaler_statistics.json | PASS |

## PHẦN 10 — CANDIDATE DEFINITIONS

| Candidate | Numeric pipeline | Missing indicators | Outlier strategy | Encoder | Scaler | Intended models |
|---|---|---|---|---|---|---|
| P22-A | Default | No | None | OneHotEncoder | StandardScaler | Linear/NN |
| P22-B | Default | Yes | None | OneHotEncoder | StandardScaler | Linear/NN |
| P22-C | Default | No | IQR | OneHotEncoder | RobustScaler | Linear/NN |
| P22-D | Default | No | None | OrdinalEncoder | None | Tree-based |

## PHẦN 11 — CANDIDATE OUTPUT SCHEMAS

| Candidate | Train shape | Validation shape | Test shape | Output features | Matrix type | NaN | Inf | Status |
|---|---|---|---|---:|---|---|---|---|
| P22-A | [415524, 56] | [85272, 56] | [85876, 56] | 56 | sparse/dense | False | False | PASS |
| P22-B | [415524, 59] | [85272, 59] | [85876, 59] | 59 | sparse/dense | False | False | PASS |
| P22-C | [415524, 56] | [85272, 56] | [85876, 56] | 56 | sparse/dense | False | False | PASS |
| P22-D | [415524, 18] | [85272, 18] | [85876, 18] | 18 | sparse/dense | False | False | PASS |

## PHẦN 12 — COMPONENT-LEVEL LEAKAGE AUDIT

| Candidate | Component | Type | Fit split | Fit rows | Fit-input hash | Statistics hash | Val fit | Test fit | Status |
|---|---|---|---|---:|---|---|---|---|---|
| P22-A | ColumnTransformer | Pipeline | train | 415524 | NOT_AVAILABLE | NOT_AVAILABLE | False | False | PASS |
| P22-B | ColumnTransformer | Pipeline | train | 415524 | NOT_AVAILABLE | NOT_AVAILABLE | False | False | PASS |
| P22-C | ColumnTransformer | Pipeline | train | 415524 | NOT_AVAILABLE | NOT_AVAILABLE | False | False | PASS |
| P22-D | ColumnTransformer | Pipeline | train | 415524 | NOT_AVAILABLE | NOT_AVAILABLE | False | False | PASS |

## PHẦN 13 — VALIDATION RESULTS

| Field | Value |
|---|---:|
| Total checks | 61 |
| Passed | 61 |
| Failed | 0 |
| Warnings | 0 |
| Blockers | 0 |

| Check ID | Task | Description | Expected | Actual | Evidence path | Pointer | Status |
|---|---|---|---|---|---|---|---|
| INPUT-ROWS | 2.2.1 | Validate rows contract | 586672 | 586672 | 5.DATA/processed/ml_ready_dataset.parquet | df.shape[0] | PASS |
| INPUT-COLUMNS | 2.2.1 | Validate columns contract | 20 | 20 | 5.DATA/processed/ml_ready_dataset.parquet | df.shape[1] | PASS |
| INPUT-IDENTIFIER | 2.2.1 | Validate identifier contract | track_id | track_id | 5.DATA/processed/ml_ready_dataset.parquet | df.columns | PASS |
| INPUT-TARGET | 2.2.1 | Validate target contract | target_popularity | target_popularity | 5.DATA/processed/ml_ready_dataset.parquet | df.columns | PASS |
| INPUT-TRAIN_ROWS | 2.2.1 | Validate train_rows contract | 415524 | 415524 | 7.ML/7.4.splits/train_ids.parquet | len(train_ids) | PASS |
| SEMANTIC-18-FEATURES | 2.2.2 | Exactly 18 input features classified | 18 | 18 | 5.DATA/processed/ml_ready_dataset.parquet | input_feature_count | PASS |
| IMPUTE-TEMPO-TRAIN-ONLY | 2.2.3 | Imputer for tempo fitted on train only | train | train | 7.ML/7.5.preprocessing/imputer_statistics.json | fitted_on_split | PASS |
| IMPUTE-TIME_SIGNATURE-TRAIN-ONLY | 2.2.3 | Imputer for time_signature fitted on train only | train | train | 7.ML/7.5.preprocessing/imputer_statistics.json | fitted_on_split | PASS |
| OUTLIER-DURATION_MIN-TRAIN-ONLY | 2.2.4 | Outlier thresholds for duration_min computed from train only | train | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | fitted_on_split | PASS |
| OUTLIER-TEMPO-TRAIN-ONLY | 2.2.4 | Outlier thresholds for tempo computed from train only | train | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | fitted_on_split | PASS |
| OUTLIER-LOUDNESS-TRAIN-ONLY | 2.2.4 | Outlier thresholds for loudness computed from train only | train | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | fitted_on_split | PASS |
| ENCODE-P22-A-RELEASE_MONTH-TRAIN-ONLY | 2.2.5 | Encoder categories for release_month fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-DECADE-TRAIN-ONLY | 2.2.5 | Encoder categories for decade fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-RELEASE_PRECISION-TRAIN-ONLY | 2.2.5 | Encoder categories for release_precision fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-KEY-TRAIN-ONLY | 2.2.5 | Encoder categories for key fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-A-TIME_SIGNATURE-TRAIN-ONLY | 2.2.5 | Encoder categories for time_signature fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-RELEASE_MONTH-TRAIN-ONLY | 2.2.5 | Encoder categories for release_month fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-DECADE-TRAIN-ONLY | 2.2.5 | Encoder categories for decade fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-RELEASE_PRECISION-TRAIN-ONLY | 2.2.5 | Encoder categories for release_precision fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-KEY-TRAIN-ONLY | 2.2.5 | Encoder categories for key fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-B-TIME_SIGNATURE-TRAIN-ONLY | 2.2.5 | Encoder categories for time_signature fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-RELEASE_MONTH-TRAIN-ONLY | 2.2.5 | Encoder categories for release_month fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-DECADE-TRAIN-ONLY | 2.2.5 | Encoder categories for decade fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-RELEASE_PRECISION-TRAIN-ONLY | 2.2.5 | Encoder categories for release_precision fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-KEY-TRAIN-ONLY | 2.2.5 | Encoder categories for key fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-C-TIME_SIGNATURE-TRAIN-ONLY | 2.2.5 | Encoder categories for time_signature fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-RELEASE_MONTH-TRAIN-ONLY | 2.2.5 | Encoder categories for release_month fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-DECADE-TRAIN-ONLY | 2.2.5 | Encoder categories for decade fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-RELEASE_PRECISION-TRAIN-ONLY | 2.2.5 | Encoder categories for release_precision fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-KEY-TRAIN-ONLY | 2.2.5 | Encoder categories for key fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| ENCODE-P22-D-TIME_SIGNATURE-TRAIN-ONLY | 2.2.5 | Encoder categories for time_signature fitted on train only | train | train | 7.ML/7.5.preprocessing/encoder_categories.json | fit_split | PASS |
| SCALE-P22-A-DURATION_MIN-TRAIN-ONLY | 2.2.6 | Scaler statistics for duration_min fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-RELEASE_YEAR-TRAIN-ONLY | 2.2.6 | Scaler statistics for release_year fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-DANCEABILITY-TRAIN-ONLY | 2.2.6 | Scaler statistics for danceability fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-ENERGY-TRAIN-ONLY | 2.2.6 | Scaler statistics for energy fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-LOUDNESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for loudness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-SPEECHINESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for speechiness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-ACOUSTICNESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for acousticness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-INSTRUMENTALNESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for instrumentalness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-LIVENESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for liveness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-VALENCE-TRAIN-ONLY | 2.2.6 | Scaler statistics for valence fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-A-TEMPO-TRAIN-ONLY | 2.2.6 | Scaler statistics for tempo fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-DURATION_MIN-TRAIN-ONLY | 2.2.6 | Scaler statistics for duration_min fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-RELEASE_YEAR-TRAIN-ONLY | 2.2.6 | Scaler statistics for release_year fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-DANCEABILITY-TRAIN-ONLY | 2.2.6 | Scaler statistics for danceability fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-ENERGY-TRAIN-ONLY | 2.2.6 | Scaler statistics for energy fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-LOUDNESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for loudness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-SPEECHINESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for speechiness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-ACOUSTICNESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for acousticness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-INSTRUMENTALNESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for instrumentalness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-LIVENESS-TRAIN-ONLY | 2.2.6 | Scaler statistics for liveness fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-VALENCE-TRAIN-ONLY | 2.2.6 | Scaler statistics for valence fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCALE-P22-C-TEMPO-TRAIN-ONLY | 2.2.6 | Scaler statistics for tempo fitted on train only | train | train | 7.ML/7.5.preprocessing/scaler_statistics.json | fit_split | PASS |
| SCHEMA-P22-A-NO-NAN | 2.2.7 | P22-A output contains no NaN | False | False | 7.ML/7.5.preprocessing/p22_a/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-A-NO-INF | 2.2.7 | P22-A output contains no Inf | False | False | 7.ML/7.5.preprocessing/p22_a/output_schema.json | contains_inf | PASS |
| SCHEMA-P22-B-NO-NAN | 2.2.7 | P22-B output contains no NaN | False | False | 7.ML/7.5.preprocessing/p22_b/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-B-NO-INF | 2.2.7 | P22-B output contains no Inf | False | False | 7.ML/7.5.preprocessing/p22_b/output_schema.json | contains_inf | PASS |
| SCHEMA-P22-C-NO-NAN | 2.2.7 | P22-C output contains no NaN | False | False | 7.ML/7.5.preprocessing/p22_c/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-C-NO-INF | 2.2.7 | P22-C output contains no Inf | False | False | 7.ML/7.5.preprocessing/p22_c/output_schema.json | contains_inf | PASS |
| SCHEMA-P22-D-NO-NAN | 2.2.7 | P22-D output contains no NaN | False | False | 7.ML/7.5.preprocessing/p22_d/output_schema.json | contains_nan | PASS |
| SCHEMA-P22-D-NO-INF | 2.2.7 | P22-D output contains no Inf | False | False | 7.ML/7.5.preprocessing/p22_d/output_schema.json | contains_inf | PASS |

## PHẦN 14 — PYTEST VÀ JUNIT

| Field | Value |
|---|---|
| Collected | 11 |
| Passed | 11 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration | 0.074 |
| Pytest version | 9.1.1 |
| JUnit path | 7.ML/7.5.preprocessing/pytest_feature_2_2.xml |
| JUnit full SHA-256 | d33795d2725cf5e4f2f8af6dc99892b3e6a9cb2d69c10bdfae633a08744637c7 |

| Test file | Test case | Result | Duration |
|---|---|---|---:|
| tests.test_feature_2_2_preprocessing | test_input_contract | PASS | 0.001 |
| tests.test_feature_2_2_preprocessing | test_semantic_roles | PASS | 0.001 |
| tests.test_feature_2_2_preprocessing | test_output_schema_P22A | PASS | 0.001 |
| tests.test_feature_2_2_preprocessing | test_output_schema_P22B | PASS | 0.001 |
| tests.test_feature_2_2_preprocessing | test_output_schema_P22C | PASS | 0.001 |
| tests.test_feature_2_2_preprocessing | test_output_schema_P22D | PASS | 0.001 |
| tests.test_feature_2_2_leakage_safety | test_leakage_audit | PASS | 0.001 |
| tests.test_feature_2_2_leakage_safety | test_imputer_leakage | PASS | 0.001 |
| tests.test_feature_2_2_leakage_safety | test_outlier_leakage | PASS | 0.001 |
| tests.test_feature_2_2_artifacts | test_json_artifacts_exist | PASS | 0.001 |
| tests.test_feature_2_2_artifacts | test_models_exist | PASS | 0.001 |

## PHẦN 15 — ARTIFACT MANIFEST

| Path | Category | Exists | Valid | Bytes | Full SHA-256 | Modified at |
|---|---|---|---|---:|---|---|
| 7.ML\7.5.preprocessing\feature_2_2_generation_context.json | JSON | True | True | 737 | 22a079bede70b7ba2c7295b8fdbff5489aa0363bef61f7fc2eb69b131e8b166a | 2026-07-18T17:29:26.295552 |
| 7.ML\7.5.preprocessing\preprocessing_input_contract.json | JSON | True | True | 1275 | 3414b49f54b09ad973e6630b8bcde8ed25f30414084553c157f60ad4217ed4bd | 2026-07-18T17:29:27.248599 |
| 7.ML\7.5.preprocessing\semantic_roles.json | JSON | True | True | 1497 | 783fc5f15bd2fe62832a9a7913a2fd4ff8092f1a0cf57a31c513bae8117b2007 | 2026-07-18T17:29:27.249127 |
| 7.ML\7.5.preprocessing\missing_profile_by_split.json | JSON | True | True | 419 | b06c20b5011cbebc062ef1a0d5ca8e1f28ed152ed5200b391506c43f56395635 | 2026-07-18T17:29:37.480413 |
| 7.ML\7.5.preprocessing\missing_value_strategy.json | JSON | True | True | 491 | a698ad6efd320e70eb3a632d5c2b9509d289c17d32cab9448f43fa2731a1bc2a | 2026-07-18T17:29:37.480927 |
| 7.ML\7.5.preprocessing\imputer_statistics.json | JSON | True | True | 839 | 8a41941cad345d1e87ce605a5504cbd86c7748038b776e4abbfa4db92b434684 | 2026-07-18T17:29:37.575798 |
| 7.ML\7.5.preprocessing\outlier_config.json | JSON | True | True | 82 | 3966ce962d35cd9f294d3c17d3cd966264cf061f2f618e83b66083d7a00c600b | 2026-07-18T17:32:17.104544 |
| 7.ML\7.5.preprocessing\outlier_thresholds.json | JSON | True | True | 1902 | 0ebb000fe4359b1e486600db75fbe5d257e2dde0530d2936f6bc8db39bd51319 | 2026-07-18T17:29:37.752302 |
| 7.ML\7.5.preprocessing\outlier_profile_by_split.json | JSON | True | True | 67 | bc8629508d2eecae7cdbbbf0bf234536e31a428fe3c17028d0f61223ba4d33a8 | 2026-07-18T17:32:17.105066 |
| 7.ML\7.5.preprocessing\encoding_config.json | JSON | True | True | 52 | cab655673fe42c50c0b8d9de349e3aa0b747d7a1e2c5e7a3550a6bd28cd888d4 | 2026-07-18T17:32:17.105066 |
| 7.ML\7.5.preprocessing\encoder_categories.json | JSON | True | True | 8642 | 043e804a3781ebd049568504b7a65981972513b5a852c755e0c6536d960a0729 | 2026-07-18T17:31:41.497720 |
| 7.ML\7.5.preprocessing\unknown_category_profile.json | JSON | True | True | 2442 | 43c9c52d63a1954ca0682cf216e878991d2a7d82490a65f09d7b42c47746b984 | 2026-07-18T17:29:37.824294 |
| 7.ML\7.5.preprocessing\scaling_config.json | JSON | True | True | 34 | b41b79c504fd2ca74bb93409019200c18cbe6d797df83f4d3c6f11c672ff658f | 2026-07-18T17:32:17.105585 |
| 7.ML\7.5.preprocessing\scaler_statistics.json | JSON | True | True | 7502 | dfe5dd1c8cd769cc348e41763ffc1ca6d738b3fadf970a4125f0267d43790131 | 2026-07-18T17:31:41.499284 |
| 7.ML\7.5.preprocessing\preprocessing_fit_audit.json | JSON | True | True | 2127 | 0b65a495d82102d1d3ab181335e042f2367e230a7326b3713c82cc9efab6da6b | 2026-07-18T17:31:41.496163 |
| 7.ML\7.5.preprocessing\preprocessing_validation_results.json | JSON | True | True | 34005 | f893e6aed9b193dbff132c5c76f36f363ccd0b9ecae0bd17038af354fb3c6455 | 2026-07-18T17:31:06.658827 |
| 7.ML\7.5.preprocessing\feature_2_2_test_summary.json | JSON | True | True | 757 | 44e9d9454cda6a3c77dd769f935de589095b0c4866654b01cba1d3dd0141e11a | 2026-07-18T17:32:37.188880 |
| 7.ML\7.5.preprocessing\feature_2_2_report_manifest.json | JSON | True | True | 3820 | 5aeb8bc909f198fdffd0119c164017a2a89ef49a46e7188852dc1af91f41a954 | 2026-07-18T17:33:35.735240 |
| 7.ML\7.5.preprocessing\feature_2_2_closure_gate.json | JSON | True | True | 958 | 0284af5777accf714d086730ee2939aeb845327b2b9b90600d62123b64bcb56f | 2026-07-18T17:33:35.735745 |
| 7.ML\7.5.preprocessing\report_source_map.json | JSON | True | True | 869 | 754f113fc96a30edcc2d27a68364c7287f96efbcd74649b9879d0cb31e95fa34 | 2026-07-18T17:33:13.120171 |

## PHẦN 16 — REPORT–ARTIFACT CONSISTENCY

| Report | Claim/field | Markdown value | Artifact value | Source | Match | Status |
|---|---|---|---|---|---|---|
| TEST_COVERAGE_REPORT.md | Tests Passed | 11 | 11 | pytest_feature_2_2.xml | True | MATCH |

## PHẦN 17 — REPORT SOURCE MAP

| Review-package field | Rendered value | Source artifact | JSON/XML pointer | Validation check | Testcase |
|---|---|---|---|---|---|
| Missing | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |

## PHẦN 18 — CLOSURE GATE

| Gate | Expected | Actual | Direct evidence | Status |
|---|---|---|---|---|
| input_contract_valid | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| exactly_18_features | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| feature_2_1_split_reused | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| imputer_train_only | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| encoder_train_only | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| scaler_train_only | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| outlier_thresholds_train_only | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| kmeans_train_only_or_not_applicable | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| validation_transform_only | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| test_transform_only | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| unknown_categories_safe | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| output_schema_consistent | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| no_unexpected_nan | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| no_inf | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| serialization_valid | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| reproducibility_valid | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| validation_evidence_complete | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| report_manifest_complete | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| report_source_map_complete | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |
| completion_generated_after_evidence | True | True | 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json | PASS |

## PHẦN 19 — WARNINGS VÀ BLOCKERS

| Warning ID | Description | Severity | Evidence | Owner | Carry-forward feature |
|---|---|---|---|---|---|
| REPRODUCIBILITY_RISK | Working tree is dirty | HIGH | git status | System | 2.5 |

| Blocker ID | Description | Evidence | Required fix | Blocks closure |
|---|---|---|---|---|
| None | None | None | None | None |

## PHẦN 20 — RAW ARTIFACT SNAPSHOTS

### feature_2_2_generation_context.json
```json
{
  "repository_url": "https://github.com/tandat1512/hitradar.git",
  "source_branch": "main",
  "source_commit_sha": "1352fc050d73796e67620d5fd63d44661f2172f2",
  "source_commit_timestamp": "2026-07-18 14:29:58 +0700",
  "source_commit_message": "feat(feature_2_1): finalize closure hotfix, dynamic reporting, evidence paths, and manifest artifacts",
  "working_tree_status": "DIRTY",
  "generation_started_at": "2026-07-18T10:29:26.294658+00:00",
  "generator_path": "9.SCRIPTS/feature_2_2_preprocessing.py",
  "generator_sha256": "02b55614914e1e0a5eb71482aa8c7acf921dcac4959bb14d76f3eae735cd0389",
  "python_version": "3.13.7",
  "pandas_version": "3.0.3",
  "numpy_version": "2.2.3",
  "scikit_learn_version": "1.6.1"
}
```

### preprocessing_input_contract.json
```json
{
  "data_version": "ml-ready-2026-07-17-v1",
  "split_version": "temporal-split-v1",
  "checks": [
    {
      "field": "rows",
      "expected": 586672,
      "actual": 586672,
      "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
      "evidence_pointer": "df.shape[0]",
      "status": "PASS"
    },
    {
      "field": "columns",
      "expected": 20,
      "actual": 20,
      "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
      "evidence_pointer": "df.shape[1]",
      "status": "PASS"
    },
    {
      "field": "identifier",
      "expected": "track_id",
      "actual": "track_id",
      "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
      "evidence_pointer": "df.columns",
      "status": "PASS"
    },
    {
      "field": "target",
      "expected": "target_popularity",
      "actual": "target_popularity",
      "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
      "evidence_pointer": "df.columns",
      "status": "PASS"
    },
    {
      "field": "train_rows",
      "expected": 415524,
      "actual": 415524,
      "evidence_path": "7.ML/7.4.splits/train_ids.parquet",
      "evidence_pointer": "len(train_ids)",
      "status": "PASS"
    }
  ]
}
```

### semantic_roles.json
```json
{
  "expected_continuous": [
    "duration_min",
    "release_year",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
  ],
  "expected_categorical": [
    "release_month",
    "decade",
    "release_precision",
    "key",
    "time_signature"
  ],
  "expected_binary": [
    "explicit",
    "mode"
  ],
  "actual_dataset_columns": [
    "track_id",
    "target_popularity",
    "duration_min",
    "explicit",
    "release_year",
    "release_month",
    "decade",
    "release_precision",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature"
  ],
  "missing_features": [],
  "extra_features": [],
  "input_feature_count": 18,
  "continuous": [
    "duration_min",
    "release_year",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo"
  ],
  "categorical": [
    "release_month",
    "decade",
    "release_precision",
    "key",
    "time_signature"
  ],
  "binary": [
    "explicit",
    "mode"
  ],
  "identifier": "track_id",
  "target": "target_popularity",
  "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
  "validation_status": "PASS"
}
```

### missing_profile_by_split.json
```json
{
  "tempo": {
    "total_missing": 328,
    "train_missing": 154,
    "validation_missing": 34,
    "test_missing": 140
  },
  "time_signature": {
    "total_missing": 337,
    "train_missing": 160,
    "validation_missing": 36,
    "test_missing": 141
  },
  "release_month": {
    "total_missing": 136489,
    "train_missing": 126895,
    "validation_missing": 8455,
    "test_missing": 1139
  }
}
```

### missing_value_strategy.json
```json
{
  "tempo": {
    "imputation": "median",
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
  },
  "time_signature": {
    "imputation": "most_frequent",
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
  },
  "release_month": {
    "imputation": "explicit_missing_category",
    "fit_split": "N/A",
    "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
  }
}
```

### imputer_statistics.json
```json
[
  {
    "candidate_id": "ALL",
    "column": "tempo",
    "strategy": "median",
    "fitted_value": 114.995,
    "fitted_on_split": "train",
    "fit_row_count": 415524,
    "fit_input_hash": "5c3eb338f4e0c3516d0f9bd7d83c044169c471eded610bb8b0e32fc3156b8bb9",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
  },
  {
    "candidate_id": "ALL",
    "column": "time_signature",
    "strategy": "most_frequent",
    "fitted_value": 4,
    "fitted_on_split": "train",
    "fit_row_count": 415524,
    "fit_input_hash": "5c3eb338f4e0c3516d0f9bd7d83c044169c471eded610bb8b0e32fc3156b8bb9",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
  }
]
```

### outlier_config.json
```json
{"columns": ["duration_min", "tempo", "loudness"], "method": "iqr", "factor": 1.5}
```

### outlier_thresholds.json
```json
[
  {
    "column": "duration_min",
    "method": "TRAIN_IQR_CLIP",
    "lower_threshold": 0.3898999999999999,
    "upper_threshold": 6.8683000000000005,
    "train_row_count": 415524,
    "train_outlier_count": 17647,
    "validation_outlier_count_before_transform": 2452,
    "test_outlier_count_before_transform": 1953,
    "values_clipped_by_split": {
      "train": 17647,
      "validation": 2452,
      "test": 1953
    },
    "fitted_on_split": "train",
    "fit_input_hash": "5c3eb338f4e0c3516d0f9bd7d83c044169c471eded610bb8b0e32fc3156b8bb9",
    "evidence_path": "7.ML/7.5.preprocessing/outlier_thresholds.json"
  },
  {
    "column": "tempo",
    "method": "TRAIN_IQR_CLIP",
    "lower_threshold": 33.36149999999997,
    "upper_threshold": 196.10150000000004,
    "train_row_count": 415524,
    "train_outlier_count": 4232,
    "validation_outlier_count_before_transform": 773,
    "test_outlier_count_before_transform": 620,
    "values_clipped_by_split": {
      "train": 4232,
      "validation": 773,
      "test": 620
    },
    "fitted_on_split": "train",
    "fit_input_hash": "5c3eb338f4e0c3516d0f9bd7d83c044169c471eded610bb8b0e32fc3156b8bb9",
    "evidence_path": "7.ML/7.5.preprocessing/outlier_thresholds.json"
  },
  {
    "column": "loudness",
    "method": "TRAIN_IQR_CLIP",
    "lower_threshold": -23.570875,
    "upper_threshold": 1.7541249999999993,
    "train_row_count": 415524,
    "train_outlier_count": 10265,
    "validation_outlier_count_before_transform": 444,
    "test_outlier_count_before_transform": 797,
    "values_clipped_by_split": {
      "train": 10265,
      "validation": 444,
      "test": 797
    },
    "fitted_on_split": "train",
    "fit_input_hash": "5c3eb338f4e0c3516d0f9bd7d83c044169c471eded610bb8b0e32fc3156b8bb9",
    "evidence_path": "7.ML/7.5.preprocessing/outlier_thresholds.json"
  }
]
```

### outlier_profile_by_split.json
```json
{"train_outliers": 0, "validation_outliers": 0, "test_outliers": 0}
```

### encoding_config.json
```json
{"candidates": ["P22-A", "P22-B", "P22-C", "P22-D"]}
```

### encoder_categories.json
```json
[
  {
    "candidate_id": "P22-A",
    "column": "release_month",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 13,
    "categories": [
      "1.0",
      "10.0",
      "11.0",
      "12.0",
      "2.0",
      "3.0",
      "4.0",
      "5.0",
      "6.0",
      "7.0",
      "8.0",
      "9.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-A",
    "column": "decade",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 10,
    "categories": [
      "1900",
      "1920",
      "1930",
      "1940",
      "1950",
      "1960",
      "1970",
      "1980",
      "1990",
      "2000"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-A",
    "column": "release_precision",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 3,
    "categories": [
      "day",
      "month",
      "year"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-A",
    "column": "key",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 12,
    "categories": [
      "0",
      "1",
      "10",
      "11",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-A",
    "column": "time_signature",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 5,
    "categories": [
      "1.0",
      "3.0",
      "4.0",
      "5.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-B",
    "column": "release_month",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 13,
    "categories": [
      "1.0",
      "10.0",
      "11.0",
      "12.0",
      "2.0",
      "3.0",
      "4.0",
      "5.0",
      "6.0",
      "7.0",
      "8.0",
      "9.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-B",
    "column": "decade",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 10,
    "categories": [
      "1900",
      "1920",
      "1930",
      "1940",
      "1950",
      "1960",
      "1970",
      "1980",
      "1990",
      "2000"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-B",
    "column": "release_precision",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 3,
    "categories": [
      "day",
      "month",
      "year"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-B",
    "column": "key",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 12,
    "categories": [
      "0",
      "1",
      "10",
      "11",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-B",
    "column": "time_signature",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 5,
    "categories": [
      "1.0",
      "3.0",
      "4.0",
      "5.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-C",
    "column": "release_month",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 13,
    "categories": [
      "1.0",
      "10.0",
      "11.0",
      "12.0",
      "2.0",
      "3.0",
      "4.0",
      "5.0",
      "6.0",
      "7.0",
      "8.0",
      "9.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-C",
    "column": "decade",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 10,
    "categories": [
      "1900",
      "1920",
      "1930",
      "1940",
      "1950",
      "1960",
      "1970",
      "1980",
      "1990",
      "2000"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-C",
    "column": "release_precision",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 3,
    "categories": [
      "day",
      "month",
      "year"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-C",
    "column": "key",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 12,
    "categories": [
      "0",
      "1",
      "10",
      "11",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-C",
    "column": "time_signature",
    "encoder_type": "OneHotEncoder",
    "handle_unknown": "ignore",
    "output_feature_count": 5,
    "categories": [
      "1.0",
      "3.0",
      "4.0",
      "5.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-D",
    "column": "release_month",
    "encoder_type": "OrdinalEncoder",
    "handle_unknown": "use_encoded_value",
    "unknown_value": -1,
    "output_feature_count": 1,
    "categories": [
      "1.0",
      "10.0",
      "11.0",
      "12.0",
      "2.0",
      "3.0",
      "4.0",
      "5.0",
      "6.0",
      "7.0",
      "8.0",
      "9.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-D",
    "column": "decade",
    "encoder_type": "OrdinalEncoder",
    "handle_unknown": "use_encoded_value",
    "unknown_value": -1,
    "output_feature_count": 1,
    "categories": [
      "1900",
      "1920",
      "1930",
      "1940",
      "1950",
      "1960",
      "1970",
      "1980",
      "1990",
      "2000"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-D",
    "column": "release_precision",
    "encoder_type": "OrdinalEncoder",
    "handle_unknown": "use_encoded_value",
    "unknown_value": -1,
    "output_feature_count": 1,
    "categories": [
      "day",
      "month",
      "year"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-D",
    "column": "key",
    "encoder_type": "OrdinalEncoder",
    "handle_unknown": "use_encoded_value",
    "unknown_value": -1,
    "output_feature_count": 1,
    "categories": [
      "0",
      "1",
      "10",
      "11",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  },
  {
    "candidate_id": "P22-D",
    "column": "time_signature",
    "encoder_type": "OrdinalEncoder",
    "handle_unknown": "use_encoded_value",
    "unknown_value": -1,
    "output_feature_count": 1,
    "categories": [
      "1.0",
      "3.0",
      "4.0",
      "5.0",
      "__MISSING__"
    ],
    "fit_split": "train",
    "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
  }
]
```

### unknown_category_profile.json
```json
[
  {
    "column": "release_month",
    "train_categories": [
      "1.0",
      "2.0",
      "3.0",
      "4.0",
      "5.0",
      "6.0",
      "7.0",
      "8.0",
      "9.0",
      "10.0",
      "11.0",
      "12.0"
    ],
    "validation_only_categories": [],
    "test_only_categories": [],
    "unknown_count_validation": 0,
    "unknown_count_test": 0,
    "handling_strategy": "handle_unknown='ignore' / unknown_value=-1",
    "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
  },
  {
    "column": "decade",
    "train_categories": [
      "1920",
      "1990",
      "1960",
      "1930",
      "1900",
      "2000",
      "1970",
      "1940",
      "1980",
      "1950"
    ],
    "validation_only_categories": [
      "2010"
    ],
    "test_only_categories": [
      "2010",
      "2020"
    ],
    "unknown_count_validation": 39587,
    "unknown_count_test": 85876,
    "handling_strategy": "handle_unknown='ignore' / unknown_value=-1",
    "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
  },
  {
    "column": "release_precision",
    "train_categories": [
      "year",
      "month",
      "day"
    ],
    "validation_only_categories": [],
    "test_only_categories": [],
    "unknown_count_validation": 0,
    "unknown_count_test": 0,
    "handling_strategy": "handle_unknown='ignore' / unknown_value=-1",
    "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
  },
  {
    "column": "key",
    "train_categories": [
      "0",
      "1",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "11"
    ],
    "validation_only_categories": [],
    "test_only_categories": [],
    "unknown_count_validation": 0,
    "unknown_count_test": 0,
    "handling_strategy": "handle_unknown='ignore' / unknown_value=-1",
    "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
  },
  {
    "column": "time_signature",
    "train_categories": [
      "1.0",
      "3.0",
      "4.0",
      "5.0"
    ],
    "validation_only_categories": [],
    "test_only_categories": [],
    "unknown_count_validation": 0,
    "unknown_count_test": 0,
    "handling_strategy": "handle_unknown='ignore' / unknown_value=-1",
    "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
  }
]
```

### scaling_config.json
```json
{"candidates": ["P22-A", "P22-C"]}
```

### scaler_statistics.json
```json
[
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "duration_min",
    "fitted_mean": 3.8246370017134987,
    "fitted_scale": 2.135581759728712,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "release_year",
    "fitted_mean": 1978.382926136637,
    "fitted_scale": 19.26276696407741,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "danceability",
    "fitted_mean": 0.544403715790183,
    "fitted_scale": 0.16539908726365904,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "energy",
    "fitted_mean": 0.495358725215872,
    "fitted_scale": 0.2503912692639482,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "loudness",
    "fitted_mean": -11.393526484631453,
    "fitted_scale": 5.076654941551704,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "speechiness",
    "fitted_mean": 0.1105506283632233,
    "fitted_scale": 0.20231939971890542,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "acousticness",
    "fitted_mean": 0.5150132032415696,
    "fitted_scale": 0.34911370719831447,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "instrumentalness",
    "fitted_mean": 0.12591107220819978,
    "fitted_scale": 0.27747216975341393,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "liveness",
    "fitted_mean": 0.21788359919041983,
    "fitted_scale": 0.18638135680726847,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "valence",
    "fitted_mean": 0.5632940204515263,
    "fitted_scale": 0.26006470223778566,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-A",
    "scaler": "StandardScaler",
    "column": "tempo",
    "fitted_mean": 117.03268697596289,
    "fitted_scale": 29.91139994600036,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "duration_min",
    "fitted_center": 3.5173,
    "fitted_scale": 1.6196000000000002,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "release_year",
    "fitted_center": 1983.0,
    "fitted_scale": 28.0,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "danceability",
    "fitted_center": 0.558,
    "fitted_scale": 0.23700000000000004,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "energy",
    "fitted_center": 0.484,
    "fitted_scale": 0.39699999999999996,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "loudness",
    "fitted_center": -10.655,
    "fitted_scale": 6.33125,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "speechiness",
    "fitted_center": 0.0429,
    "fitted_scale": 0.0361,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "acousticness",
    "fitted_center": 0.552,
    "fitted_scale": 0.6839999999999999,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "instrumentalness",
    "fitted_center": 6.22e-05,
    "fitted_scale": 0.0212,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "liveness",
    "fitted_center": 0.143,
    "fitted_scale": 0.18489999999999998,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "valence",
    "fitted_center": 0.582,
    "fitted_scale": 0.42700000000000005,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  },
  {
    "candidate_id": "P22-C",
    "scaler": "RobustScaler",
    "column": "tempo",
    "fitted_center": 114.995,
    "fitted_scale": 40.66900000000001,
    "fit_split": "train",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
  }
]
```

### preprocessing_fit_audit.json
```json
[
  {
    "candidate_id": "P22-A",
    "component_name": "P22-A",
    "component_type": "ColumnTransformer",
    "fit_split": "train",
    "fit_row_count": 415524,
    "fit_input_hash": "c3291206ba5b4bfa54f1cd34445e61191dbc2e4bc87b4c841f11e80ebf0e551a",
    "fitted_statistics_hash": "312941ecbaccfb48e20f7abec75297327f5b49610b6bca2bc490bce090437990",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/preprocessing_fit_audit.json",
    "status": "PASS"
  },
  {
    "candidate_id": "P22-B",
    "component_name": "P22-B",
    "component_type": "ColumnTransformer",
    "fit_split": "train",
    "fit_row_count": 415524,
    "fit_input_hash": "c3291206ba5b4bfa54f1cd34445e61191dbc2e4bc87b4c841f11e80ebf0e551a",
    "fitted_statistics_hash": "bac01d34c8f61db80f232f61a43760459f40537a6146fbc1aae981f30d03b1e6",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/preprocessing_fit_audit.json",
    "status": "PASS"
  },
  {
    "candidate_id": "P22-C",
    "component_name": "P22-C",
    "component_type": "ColumnTransformer",
    "fit_split": "train",
    "fit_row_count": 415524,
    "fit_input_hash": "c3291206ba5b4bfa54f1cd34445e61191dbc2e4bc87b4c841f11e80ebf0e551a",
    "fitted_statistics_hash": "fe7042fc654d30141dc60bc2b80c12939b479f4e1419eb7fb7d6f6b7db8de719",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/preprocessing_fit_audit.json",
    "status": "PASS"
  },
  {
    "candidate_id": "P22-D",
    "component_name": "P22-D",
    "component_type": "ColumnTransformer",
    "fit_split": "train",
    "fit_row_count": 415524,
    "fit_input_hash": "c3291206ba5b4bfa54f1cd34445e61191dbc2e4bc87b4c841f11e80ebf0e551a",
    "fitted_statistics_hash": "0eadb5b8b9a532d9db06333ddbc831582a6cf0868e7d59e6b9fd0cb52e585b58",
    "validation_fit_called": false,
    "test_fit_called": false,
    "evidence_path": "7.ML/7.5.preprocessing/preprocessing_fit_audit.json",
    "status": "PASS"
  }
]
```

### feature_2_2_test_summary.json
```json
{
  "generated_at": "2026-07-18T10:32:37.188498+00:00",
  "repository_url": "https://github.com/tandat1512/hitradar.git",
  "source_branch": "main",
  "source_commit_sha": "1352fc050d73796e67620d5fd63d44661f2172f2",
  "working_tree_status": "DIRTY",
  "pytest_version": "9.1.1",
  "test_files": [
    "tests/test_feature_2_2_preprocessing.py",
    "tests/test_feature_2_2_leakage_safety.py",
    "tests/test_feature_2_2_artifacts.py"
  ],
  "collected": 11,
  "passed": 11,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "duration_seconds": 0.074,
  "junit_xml_path": "7.ML/7.5.preprocessing/pytest_feature_2_2.xml",
  "junit_xml_sha256": "d33795d2725cf5e4f2f8af6dc99892b3e6a9cb2d69c10bdfae633a08744637c7",
  "overall_status": "PASS"
}
```

### feature_2_2_report_manifest.json
```json
{
  "manifest_base": "repository_root",
  "hashes": {
    "7.ML/7.5.preprocessing/feature_2_2_generation_context.json": "22a079bede70b7ba2c7295b8fdbff5489aa0363bef61f7fc2eb69b131e8b166a",
    "7.ML/7.5.preprocessing/preprocessing_input_contract.json": "3414b49f54b09ad973e6630b8bcde8ed25f30414084553c157f60ad4217ed4bd",
    "7.ML/7.5.preprocessing/semantic_roles.json": "783fc5f15bd2fe62832a9a7913a2fd4ff8092f1a0cf57a31c513bae8117b2007",
    "7.ML/7.5.preprocessing/missing_profile_by_split.json": "b06c20b5011cbebc062ef1a0d5ca8e1f28ed152ed5200b391506c43f56395635",
    "7.ML/7.5.preprocessing/missing_value_strategy.json": "a698ad6efd320e70eb3a632d5c2b9509d289c17d32cab9448f43fa2731a1bc2a",
    "7.ML/7.5.preprocessing/imputer_statistics.json": "8a41941cad345d1e87ce605a5504cbd86c7748038b776e4abbfa4db92b434684",
    "7.ML/7.5.preprocessing/outlier_profile_by_split.json": "bc8629508d2eecae7cdbbbf0bf234536e31a428fe3c17028d0f61223ba4d33a8",
    "7.ML/7.5.preprocessing/outlier_config.json": "3966ce962d35cd9f294d3c17d3cd966264cf061f2f618e83b66083d7a00c600b",
    "7.ML/7.5.preprocessing/outlier_thresholds.json": "0ebb000fe4359b1e486600db75fbe5d257e2dde0530d2936f6bc8db39bd51319",
    "7.ML/7.5.preprocessing/encoding_config.json": "cab655673fe42c50c0b8d9de349e3aa0b747d7a1e2c5e7a3550a6bd28cd888d4",
    "7.ML/7.5.preprocessing/encoder_categories.json": "043e804a3781ebd049568504b7a65981972513b5a852c755e0c6536d960a0729",
    "7.ML/7.5.preprocessing/unknown_category_profile.json": "43c9c52d63a1954ca0682cf216e878991d2a7d82490a65f09d7b42c47746b984",
    "7.ML/7.5.preprocessing/scaling_config.json": "b41b79c504fd2ca74bb93409019200c18cbe6d797df83f4d3c6f11c672ff658f",
    "7.ML/7.5.preprocessing/scaler_statistics.json": "dfe5dd1c8cd769cc348e41763ffc1ca6d738b3fadf970a4125f0267d43790131",
    "7.ML/7.5.preprocessing/preprocessing_fit_audit.json": "0b65a495d82102d1d3ab181335e042f2367e230a7326b3713c82cc9efab6da6b",
    "7.ML/7.5.preprocessing/preprocessing_validation_results.json": "f893e6aed9b193dbff132c5c76f36f363ccd0b9ecae0bd17038af354fb3c6455",
    "7.ML/7.5.preprocessing/feature_2_2_test_summary.json": "44e9d9454cda6a3c77dd769f935de589095b0c4866654b01cba1d3dd0141e11a",
    "7.ML/7.5.preprocessing/report_source_map.json": "754f113fc96a30edcc2d27a68364c7287f96efbcd74649b9879d0cb31e95fa34",
    "7.ML/7.5.preprocessing/p22_a/output_schema.json": "dd7921897d124dff309ebd79d2c7579d0dc3a1c22d6a0995fc365c9b201e6df2",
    "7.ML/7.5.preprocessing/p22_a/feature_names.json": "a09409a383bffd1b5d7e11d5e39de95539bf6a09068a0c5f5d85af5ad279457b",
    "7.ML/7.5.preprocessing/p22_a/preprocessor.joblib": "25efcbeddfff6834106225bcc612f1d0045f709b25bd7bf0325ec77fd780a37f",
    "7.ML/7.5.preprocessing/p22_b/output_schema.json": "0a5a4da84b4d66ebd697fa89917cac23a63fc60a7ea904be33c41d3826947fbb",
    "7.ML/7.5.preprocessing/p22_b/feature_names.json": "00db1f282fc2164abd3763beac9a49438c2e09ed7c725271ae339f8fbbf61889",
    "7.ML/7.5.preprocessing/p22_b/preprocessor.joblib": "8541608976d6b97e245bd04bd03cb119e67ea409be63c658ab57d32e9687e3a8",
    "7.ML/7.5.preprocessing/p22_c/output_schema.json": "294c84bcce2aec4e060189be587d02b96b901130af7d23703256bae1cec644e0",
    "7.ML/7.5.preprocessing/p22_c/feature_names.json": "a09409a383bffd1b5d7e11d5e39de95539bf6a09068a0c5f5d85af5ad279457b",
    "7.ML/7.5.preprocessing/p22_c/preprocessor.joblib": "1bdd0bebe350ea330687c1b5b1ac4af7822826124f20094e64222aa7235c9fc5",
    "7.ML/7.5.preprocessing/p22_d/output_schema.json": "933d1621ff145f98b4e3a299b6f2204c94eeeeaf3f914f6af223d3dc4630730b",
    "7.ML/7.5.preprocessing/p22_d/feature_names.json": "ab82b45d5cde703717e3ef1685419af22801bfe011267b64733b3c448406eb8a",
    "7.ML/7.5.preprocessing/p22_d/preprocessor.joblib": "ac86ce5ce20eceac40efe128d37bd1cf5ab548647e7471255f426bf7ad8034ac"
  }
}
```

### feature_2_2_closure_gate.json
```json
{
  "feature_id": "2.2",
  "input_contract_valid": true,
  "exactly_18_features": true,
  "feature_2_1_split_reused": true,
  "imputer_train_only": true,
  "encoder_train_only": true,
  "scaler_train_only": true,
  "outlier_thresholds_train_only": true,
  "kmeans_train_only_or_not_applicable": true,
  "validation_transform_only": true,
  "test_transform_only": true,
  "unknown_categories_safe": true,
  "output_schema_consistent": true,
  "no_unexpected_nan": true,
  "no_inf": true,
  "serialization_valid": true,
  "reproducibility_valid": true,
  "validation_evidence_complete": true,
  "tests_failed": 0,
  "tests_errors": 0,
  "validation_failed": 0,
  "report_manifest_complete": true,
  "report_source_map_complete": true,
  "completion_generated_after_evidence": true,
  "blocking_items": [],
  "final_status": "PASS_WITH_WARNINGS",
  "feature_2_2_decision": "ELIGIBLE_FOR_CLOSURE",
  "feature_2_3_gate": "MAY_BEGIN"
}
```

### report_source_map.json
```json
{
  "MISSING_VALUE_STRATEGY_REPORT.md": {
    "tempo_train_median": {
      "value": 114.995,
      "source_path": "7.ML/7.5.preprocessing/imputer_statistics.json",
      "source_pointer": "#/0/fitted_value"
    },
    "tempo_total_missing": {
      "value": 328,
      "source_path": "7.ML/7.5.preprocessing/missing_profile_by_split.json",
      "source_pointer": "#/tempo/total_missing"
    }
  },
  "OUTLIER_PREPROCESSING_REPORT.md": {
    "duration_min_lower": {
      "value": 0.3898999999999999,
      "source_path": "7.ML/7.5.preprocessing/outlier_thresholds.json",
      "source_pointer": "#/0/lower_threshold"
    }
  },
  "PREPROCESSING_VALIDATION_REPORT.md": {
    "total_checks": {
      "value": 61,
      "source_path": "7.ML/7.5.preprocessing/preprocessing_validation_results.json",
      "source_pointer": "length"
    }
  }
}
```


## PHẦN 21 — FINAL DECISION

| Field | Value |
|---|---|
| Core implementation | COMPLETE |
| Artifact completeness | COMPLETE |
| Report consistency | MATCH |
| Leakage-safety evidence | PASS |
| Validation evidence | 61/61 |
| Test evidence | 11/11 |
| Manifest status | VALID |
| Closure status | PASS_WITH_WARNINGS |
| Remaining warnings | 1 |
| Remaining blockers | 0 |
| Feature 2.2 decision | ELIGIBLE_FOR_CLOSURE |
| Feature 2.3 formal gate | MAY_BEGIN |
