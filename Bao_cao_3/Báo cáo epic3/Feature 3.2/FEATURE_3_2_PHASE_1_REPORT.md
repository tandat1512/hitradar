# Feature 3.2 — FastAPI Backend — Phase 1 Report
**Feature:** 3.2 — FastAPI Backend
**Phase:** 1 / 6
**Person in Charge:** Minh
**Date:** 2026-08-05
**Status:** PASS

---

## 1. Mục tiêu Phase 1

Xây dựng project structure, configuration management, và Pydantic schemas cho FastAPI backend.

---

## 2. Deliverables

### 2.1 Project Structure

```
5.UNG_DUNG/5.1.backend_api/
├── api.py                    # FastAPI app, routes, lifespan
├── config.py                # Configuration management
├── pipeline_loader.py        # Singleton model loader
├── runtime_patches.py        # 4 runtime patches (from Feature 3.1)
├── requirements.txt        # Dependencies
├── run.bat                  # Startup script
├── models/
│   └── prediction.py       # Pydantic models
└── utils/
    ├── database.py
    └── helpers.py
```

### 2.2 Configuration (`config.py`)

| Variable | Value | Notes |
|---|---|---|
| `BASE_DIR` | Resolved from `__file__` | Not hardcoded |
| `ARTIFACTS_DIR` | `BASE_DIR / "artifacts" / "epic2"` | Resolved |
| `ARTIFACTS_PATH` | From `ARTIFACTS_DIR` or env `ARTIFACTS_PATH` | Overridable |
| `SHAP_DIR` | `BASE_DIR / "7.ML" / "7.9.explainability"` | SHAP assets |
| `RUNTIME_DIR` | `ARTIFACTS_PATH / "runtime"` | |
| `SCHEMAS_DIR` | `ARTIFACTS_PATH / "schemas"` | |
| `EXAMPLES_DIR` | `ARTIFACTS_PATH / "examples"` | |
| `METADATA_DIR` | `ARTIFACTS_PATH / "metadata"` | |
| `FE_TRANSFORMERS_PATH` | EPIC 2 transformers path | For patching |

### 2.3 Pydantic Schemas (`models/prediction.py`)

| Schema | Fields | Notes |
|---|---|---|
| `PredictRequest` | 18 fields | Matches input_schema.json |
| `PredictResponse` | 9 fields | status, prediction_raw, clipped, display, warnings, ids, timestamp |
| `ExplainResponse` | 9 fields | + base_value, shap_values dict, top_features list |
| `WhatIfRequest` | base_features + changed_features | |
| `WhatIfResponse` | before/after PredictionShort + delta | |
| `HealthResponse` | status, model_loaded, timestamp | |
| `ModelInfoResponse` | model metadata + Metrics (MAE/RMSE/R2) | |
| `FeaturesResponse` | canonical_fields + selected_features | |
| `FieldDescriptor` | name, position, type, constraints | |
| `TopFeature` | name, shap_value, feature_value | |
| `PredictionShort` | raw, clipped, display | |
| `Metrics` | MAE, RMSE, R2 | nullable |

### 2.4 Runtime Patches

4 patches được áp dụng tại startup (từ Feature 3.1):

| # | Patch | Purpose |
|---|---|---|
| 1 | `transformers` → EPIC2 `FeatureEngineeringTransformer` | Resolve module name conflict |
| 2 | `__main__.to_string` → safe converter | Fix ColumnTransformer serialization |
| 3 | `sys.path` insertion | Enable module resolution |
| 4 | `fit()` interception | No-refit guard |

### 2.5 PipelineLoader Singleton

- Eager-loads `full_inference_pipeline.joblib` tại startup
- Caches schemas (input_schema, selected_features)
- Caches metadata (model_version, data_version, package_version)
- `is_loaded()` health check

---

## 3. API Endpoints Implemented

| Method | Path | Response Model | Status |
|---|---|---|---|
| GET | `/health` | `HealthResponse` | ✅ Implemented |
| GET | `/model-info` | `ModelInfoResponse` | ✅ Implemented |
| GET | `/features` | `FeaturesResponse` | ✅ Implemented |
| POST | `/predict` | `PredictResponse` | ✅ Implemented |
| POST | `/explain` | `ExplainResponse` | ✅ Implemented |
| POST | `/what-if` | `WhatIfResponse` | ✅ Implemented |

---

## 4. E2E Verification

Server khởi động tại `http://127.0.0.1:8766`:

```
INFO: Loading HitRadarInferencePipeline at startup ...
INFO:   [PATCH] transformers -> EPIC2 FeatureEngineeringTransformer
INFO:   [PATCH] __main__.to_string -> safe per-column converter
INFO:   [PATCH] sys.path: runtime, epic2
INFO: Pipeline loaded successfully.
INFO: Pipeline ready.
INFO: Application startup complete.
```

| Endpoint | HTTP Status | Response |
|---|---|---|
| `GET /health` | 200 | `healthy`, `model_loaded: true` |
| `GET /model-info` | 200 | `model_id: EXP24-XGB-FINAL-001` |
| `POST /predict` | 200 | `prediction_raw: 46.421062` |
| `POST /explain` | 200 | `base_value: 22.88`, top1: `release_year` |
| `POST /what-if` | 200 | `delta: -4.014` (year 1992→2020) |

---

## 5. Configuration Validation

- No hardcoded personal paths
- All paths resolved from `__file__` (relative)
- `ARTIFACTS_PATH` overridable via environment variable
- Schemas loaded from package directory, not hardcoded

---

## 6. Phase 1 Gate

| Criterion | Status |
|---|---|
| Project structure complete | ✅ |
| Config from `__file__` | ✅ |
| No hardcoded paths | ✅ |
| Pydantic schemas match input_schema | ✅ |
| Pydantic schemas match output_schema | ✅ |
| All 6 endpoints implemented | ✅ |
| PipelineLoader singleton | ✅ |
| Runtime patches applied | ✅ |
| Server starts successfully | ✅ |
| `/predict` returns correct value | ✅ (46.421062) |
| `/explain` returns SHAP values | ✅ |
| `/what-if` returns delta | ✅ |

**Phase 1 Gate: PASS — MAY BEGIN Phase 2**
