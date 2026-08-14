# Feature 3.1 — Model & Schema Validation Report
**Feature ID:** 3.1 — Inference Pipeline Artifact Validation
**Phase:** 2/5 — Model Loading & Schema Parsing
**Session:** F31-P1-INTAKE-20260803-204512-MINH
**Generated:** 2026-08-03T21:44:00+07:00
**Status:** PASS_WITH_WARNINGS

---

## 1. Model Artifact

| Property | Value |
|---|---|
| Artifact | `7.ML/7.10.model_packaging/package/pipeline/full_inference_pipeline.joblib` |
| SHA-256 | `7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99` |
| Loader | `joblib` 1.5.3 |
| Load Duration | 1849ms |
| Load Valid | YES |
| Hash Unchanged | YES |

---

## 2. Loaded Pipeline Object

| Property | Value |
|---|---|
| Object Type | `inference_pipeline.HitRadarInferencePipeline` |
| Module | `inference_pipeline` |
| Main API | `predict_popularity()` |
| `predict()` available | YES |
| `predict_proba()` available | NO (XGBRegressor is a regressor) |
| `transform()` available | NO (wrapper is a predictor) |
| `champion_pipeline` type | `sklearn.pipeline.Pipeline` |
| `n_features_in_` exposed | NO (wrapper returns None; inner pipeline has n=18) |
| Model ID | `EXP24-XGB-FINAL-001` |
| Model Version | `1.0.0` |
| Package Version | `1.0.0` |

---

## 3. Input Schema

**File:** `schemas/input_schema.json`
**Schema ID:** `HITRADAR-PREDICTION-INPUT-V1`
**Version:** `1.0.0`
**Field Count:** 18
**Additional Properties Policy:** `IGNORE_WITH_WARNING`

### 3.1 Field Summary

| # | Field Name | Type | Required | Nullable | Default Policy |
|---|---|---|---|---|---|
| 1 | duration_min | number | YES | YES | PIPELINE_IMPUTE |
| 2 | explicit | boolean | YES | YES | PIPELINE_IMPUTE |
| 3 | release_year | integer | YES | YES | PIPELINE_IMPUTE |
| 4 | release_month | integer | YES | YES | PIPELINE_IMPUTE |
| 5 | decade | string | YES | YES | PIPELINE_IMPUTE |
| 6 | release_precision | string | YES | YES | PIPELINE_IMPUTE |
| 7 | danceability | number | YES | YES | PIPELINE_IMPUTE |
| 8 | energy | number | YES | YES | PIPELINE_IMPUTE |
| 9 | key | integer | YES | YES | PIPELINE_IMPUTE |
| 10 | loudness | number | YES | YES | PIPELINE_IMPUTE |
| 11 | mode | integer | YES | YES | PIPELINE_IMPUTE |
| 12 | speechiness | number | YES | YES | PIPELINE_IMPUTE |
| 13 | acousticness | number | YES | YES | PIPELINE_IMPUTE |
| 14 | instrumentalness | number | YES | YES | PIPELINE_IMPUTE |
| 15 | liveness | number | YES | YES | PIPELINE_IMPUTE |
| 16 | valence | number | YES | YES | PIPELINE_IMPUTE |
| 17 | tempo | number | YES | YES | PIPELINE_IMPUTE |
| 18 | time_signature | number | YES | YES | PIPELINE_IMPUTE |

### 3.2 Key Range Validations

| Field | Min | Max |
|---|---|---|
| danceability | 0.0 | 1.0 |
| tempo | 0.0 | 300.0 |
| loudness | -60.0 | 0.0 |
| release_month | 1 | 12 |
| key | 0 | 11 |

**Categorical:** `release_precision` (day/month/year), `decade` (4 values)

### 3.3 Target Exclusion
- `target_popularity` — NOT in raw input fields (CORRECT)
- `track_id` — NOT in raw input fields (CORRECT)

---

## 4. Output Schema

**File:** `schemas/output_schema.json`
**Schema ID:** `HITRADAR-PREDICTION-OUTPUT-V1`
**Field Count:** 8

| # | Field Name | Type | Description |
|---|---|---|---|
| 1 | status | string | Request status (success/error) |
| 2 | prediction_raw | number | Raw XGBoost regression output |
| 3 | prediction_clipped | number | Clipped to [0, 100] |
| 4 | prediction_display | integer | Rounded integer for display |
| 5 | model_id | string | `EXP24-XGB-FINAL-001` |
| 6 | model_version | string | `1.0.0` |
| 7 | warnings | array | Input validation warnings |
| 8 | request_id | string | Unique request identifier |

---

## 5. Selected Features

**File:** `schemas/selected_features.json`
**Feature Set ID:** `FS23-SELECTED`
**Feature Count:** 31
**Layer:** `SELECTED_ENGINEERED_FEATURES`
**Composition:** 18 raw + 13 engineered features

| # | Feature | Type |
|---|---|---|
| 1 | duration_min | raw |
| 2 | release_year | raw |
| 3 | danceability | raw |
| 4 | energy | raw |
| 5 | loudness | raw |
| 6 | speechiness | raw |
| 7 | acousticness | raw |
| 8 | instrumentalness | raw |
| 9 | liveness | raw |
| 10 | valence | raw |
| 11 | tempo | raw |
| 12 | release_month | raw |
| 13 | decade | raw |
| 14 | release_precision | raw |
| 15 | key | raw |
| 16 | time_signature | raw |
| 17 | explicit | raw |
| 18 | mode | raw |
| 19 | release_month_sin | engineered |
| 20 | release_month_cos | engineered |
| 21 | year_in_decade | engineered |
| 22 | duration_log | engineered |
| 23 | duration_squared | engineered |
| 24 | energy_danceability | engineered |
| 25 | energy_valence | engineered |
| 26 | danceability_valence | engineered |
| 27 | acousticness_instrumentalness | engineered |
| 28 | energy_liveness | engineered |
| 29 | speechiness_explicit | engineered |
| 30 | tempo_danceability | engineered |
| 31 | loudness_energy | engineered |

---

## 6. Feature Names (Transformed)

**File:** `schemas/feature_names.json`
**Layer:** `TRANSFORMED_MODEL_FEATURES`
**Feature Count:** 49 (after ColumnTransformer with OneHotEncoder expansion)

| Source | Count | Features |
|---|---|---|
| Numeric (passthrough) | 26 | duration_min, release_year, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, release_month, decade, release_month_sin, release_month_cos, year_in_decade, duration_log, duration_squared, energy_danceability, energy_valence, danceability_valence, acousticness_instrumentalness, energy_liveness, speechiness_explicit, tempo_danceability, loudness_energy |
| OneHot: release_precision | 3 | release_precision_day, release_precision_month, release_precision_year |
| OneHot: key | 12 | key_0 … key_11 |
| OneHot: time_signature | 4 | time_signature_1.0, time_signature_3.0, time_signature_4.0, time_signature_5.0 |
| OneHot: explicit | 2 | explicit_False, explicit_True |
| OneHot: mode | 2 | mode_0, mode_1 |
| **Total** | **49** | |

---

## 7. Feature Layer Summary

| Layer | Count | Status |
|---|---|---|
| RAW_INPUT_FEATURES | 18 | VALID |
| SELECTED_ENGINEERED_FEATURES | 31 | VALID |
| TRANSFORMED_MODEL_FEATURES | 49 | VALID |
| All layers distinct | YES | PASS |
| selected > raw | 31 > 18 | PASS |
| transformed > selected | 49 > 31 | PASS |

**OHE Expansion:** 5 categorical fields → 23 one-hot columns added to 26 numeric columns = **49 total**

---

## 8. Runtime Patches Required

| # | Patch | Status | Reason |
|---|---|---|---|
| 1 | `transformers` module conflict | APPLIED | HuggingFace library shadowed EPIC 2 `transformers.py`; inject custom module via `spec_from_file_location` |
| 2 | `__main__.to_string` stub | APPLIED | Pipeline pickle references training script's `__main__` module; inject safe column converter |
| 3 | `sys.path` runtime resolution | APPLIED | Resolve `inference_pipeline` and package imports |
| 4 | `FunctionTransformer.to_str` post-load | APPLIED | Replace buggy `str(df)` with per-column safe converter inside ColumnTransformer |

---

## 9. Warnings

| Type | Severity | Detail |
|---|---|---|
| `SKLEARN_VERSION_MISMATCH` | WARNING | Pipeline pickled with sklearn 1.9.0, running on 1.8.0. `InconsistentVersionWarning` raised but load succeeded. |

---

## 10. Test Summary

**113 tests collected, 113 passed, 0 failed, 0 errors**

| Test File | Tests | Result |
|---|---|---|
| `test_feature_3_1_model_loader.py` | 11 | PASS |
| `test_feature_3_1_model_hash_before_after.py` | 4 | PASS |
| `test_feature_3_1_model_interface.py` | 7 | PASS |
| `test_feature_3_1_runtime_dependencies.py` | 8 | PASS |
| `test_feature_3_1_input_schema_parse.py` | 8 | PASS |
| `test_feature_3_1_input_schema_fields.py` | 13 | PASS |
| `test_feature_3_1_input_schema_target_exclusion.py` | 3 | PASS |
| `test_feature_3_1_output_schema_parse.py` | 5 | PASS |
| `test_feature_3_1_output_schema_fields.py` | 7 | PASS |
| `test_feature_3_1_selected_features.py` | 11 | PASS |
| `test_feature_3_1_feature_names.py` | 10 | PASS |
| `test_feature_3_1_feature_layers.py` | 6 | PASS |
| `test_feature_3_1_feature_count_consistency.py` | 9 | PASS |
| `test_feature_3_1_no_refit.py` | 8 | PASS |
| `test_feature_3_1_phase_2_no_source_mutation.py` | 5 | PASS |

---

## 11. Phase 2 Gate Result

| Gate Item | Result |
|---|---|
| Artifact hash unchanged | PASS |
| Model loads successfully | PASS |
| `predict_popularity()` available | PASS |
| All schemas valid | PASS |
| Feature counts consistent | PASS |
| No-refit enforcement active | PASS |
| Source artifacts unmodified | PASS |
| Training/fit calls = 0 | PASS |
| **Overall** | **PASS_WITH_WARNINGS** |

**Sklearn version mismatch** is the only warning. Does not block Phase 3.
**Next Phase (3/5) may begin.**
