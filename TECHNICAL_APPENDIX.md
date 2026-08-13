# HitRadar Pro — Technical Appendix

**Version:** 1.0.0 · **Author:** EPIC 3 Feature 3.7
**Prerequisites:** See [README.md](README.md), [HOW_TO_RUN_APP.md](HOW_TO_RUN_APP.md)

---

## 1. Purpose and Scope

This appendix documents the technical architecture, ML artifacts, and engineering decisions of HitRadar Pro for reference by developers and reviewers.

It does not reproduce the full API reference ([API_DOCUMENTATION.md](API_DOCUMENTATION.md)), user guide ([USER_MANUAL.md](USER_MANUAL.md)), or operational runbook. Those documents take precedence for end users and operators.

---

## 2. System Architecture

### Live Mode

```
User Browser
    │
    ▼
Streamlit Frontend  (port 8501)
    │  HTTP POST /predict, /explain, /what-if
    ▼
FastAPI Backend  (port 8000)
    │  Loads full_inference_pipeline.joblib at startup
    │  Runs SHAP.TreeExplainer for /explain
    ▼
Model Artifacts  (artifacts/epic2/)
```

**Key constraint:** The frontend never loads model artifacts directly. All prediction and explanation runs through the FastAPI backend.

### Dashboard Path

```
User Browser
    │
    ▼
Streamlit Frontend  (Music Trends page)
    │  Reads CSV directly from local filesystem
    ▼
5.DATA/processed/ml_ready_dataset.csv  (read-only)
7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv  (read-only)
```

The Music Trends page does not call the FastAPI backend. It reads pre-aggregated CSVs directly. It is available without the backend running.

### Offline Fallback

When `OFFLINE_DEMO_MODE=true` or the backend is unreachable:
- Predict page shows precomputed validated example(s)
- SHAP Explanation and What-If Simulator: **not available**
- Music Trends: continues to work (local CSV)

See [USER_MANUAL.md §12](USER_MANUAL.md#12-offline-demo-mode) for user-facing offline behavior.

---

## 3. Repository Architecture

```
HitRadar_Pro/
├── 5.UNG_DUNG/
│   └── 5.1.backend_api/
│       ├── api.py                 ← FastAPI app entrypoint
│       ├── config.py              ← Settings + artifact path resolution
│       ├── pipeline_loader.py      ← Eager model load at startup
│       ├── runtime_patches.py      ← EPIC 2 transformers / __main__ compat
│       └── models/
│           └── prediction.py       ← Pydantic request/response schemas
│
├── epic3/feature_3_3/frontend/
│   ├── app.py                     ← Streamlit app entrypoint
│   ├── api/
│   │   ├── client.py              ← HitRadarAPIClient (httpx)
│   │   ├── exceptions.py           ← APIClientError
│   │   └── models.py              ← Frontend-side response types
│   ├── core/
│   │   ├── config.py             ← get_settings()
│   │   ├── navigation.py          ← Page registry (7 pages)
│   │   └── session.py            ← st.session_state helpers
│   ├── components/               ← Reusable UI components
│   └── pages/
│       ├── 0_Home.py
│       ├── 1_Predict.py
│       ├── 2_Explain.py
│       ├── 3_WhatIf.py
│       ├── 4_Trends.py            ← Dashboard: reads local CSV
│       ├── 5_Model_Info.py
│       └── 6_Limitations.py
│
├── scripts/
│   ├── run_all.py                 ← Full stack launcher
│   ├── run_backend.py             ← Backend only
│   ├── run_frontend.py           ← Frontend only
│   └── _common.py                ← Shared helpers (stdlib only)
│
└── artifacts/epic2/             ← Read-only model artifacts
    ├── pipeline/
    │   └── full_inference_pipeline.joblib
    ├── schemas/
    │   ├── input_schema.json      ← 18 canonical fields
    │   ├── output_schema.json
    │   ├── selected_features.json ← 31 selected features
    │   └── feature_names.json     ← 49 transformed names
    ├── examples/
    │   ├── example_input.json      ← Canonical example input
    │   └── example_output.json    ← Canonical example output (46)
    └── metadata/
        ├── model_version.json
        ├── package_version.json
        └── artifact_manifest.json
```

---

## 4. Data Overview

**Source:** Curated Spotify-derived dataset
**Records:** 586,672 songs
**Temporal coverage:** 1900–2021
**Task:** Regression — predict `popularity` score (0–100)

The popularity metric in the dataset is a Spotify platform engagement metric (stream/engagement-based). It is not a universal measure of musical quality or commercial success. The model captures correlational patterns in this training data only.

---

## 5. Modeling Problem

**Target:** `popularity` — a continuous score (0–100).
**Task type:** Regression.
**Algorithm:** XGBoost gradient boosting regressor.
**Model ID:** `EXP24-XGB-FINAL-001`
**Version:** `1.0.0`

---

## 6. Feature Engineering and Feature Selection

The pipeline uses three distinct feature layers:

### Raw Input Features (18)
The user-supplied canonical input fields. These are validated against `input_schema.json (HITRADAR-PREDICTION-INPUT-V1)` at the API boundary.

### Selected Features (31)
After feature selection, 18 raw features plus 13 engineered features are retained. These are listed in `selected_features.json (FS23-SELECTED)` and used in SHAP explanations. Example engineered features: `danceability_valence`, `release_month_sin`, `release_month_cos`, `duration_log`, `energy_danceability`.

### Transformed Model Features (49)
The full inference pipeline applies additional transformations (e.g., one-hot encoding, polynomial features) producing a 49-column model matrix. SHAP computations operate at this layer. The 31 selected features map to 49 model matrix columns via the feature mapping artifact.

**Summary:**

| Layer | Count | Source |
|---|---|---|
| Raw input (user-supplied) | 18 | `input_schema.json` |
| Selected (after feature selection) | 31 | `selected_features.json` |
| Transformed model matrix | 49 | `feature_names.json` |

---

## 7. Final Model

**Artifact:** `full_inference_pipeline.joblib`
**SHA-256:** `7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99`
**Class:** `HitRadarInferencePipeline`
**Champion artifact hash (EPIC 2 selection):** `ea054a9b07d6feba198bdb220942e56006f18483f906a4c1363d63e66e5aaafe`

The pipeline is loaded eagerly at FastAPI startup via `PipelineLoader`. It is never modified or refitted at runtime. Validation confirmed zero `fit`/`fit_transform`/`partial_fit` calls during EPIC 3 execution (Feature 3.1 Phase 2 no-refit check).

---

## 8. Model Evaluation

**Evaluation source:** `7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json`
**Test split:** 85,876 records (held out during EPIC 2 training)
**Validation:** [epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_metrics_validation.json](epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_metrics_validation.json)

| Metric | Value | Unit |
|---|---|---|
| MAE | 17.65 | popularity points |
| RMSE | 21.01 | popularity points |
| R² | 0.070 | coefficient of determination |
| Median Absolute Error | 16.29 | popularity points |
| Mean Residual | +4.86 | popularity points (underprediction) |
| Underprediction Rate | 67.8% | proportion |

**Interpretation notes:**
- MAE of ~17.6 points on a 0–100 scale means the model's predictions are typically off by roughly 18 popularity points.
- R² of 0.07 means the model explains approximately 7% of the variance in popularity. This is low and reflects the difficulty of predicting popularity from audio features alone.
- The positive mean residual (+4.86) indicates systematic underprediction — the model tends to predict lower than the actual popularity score.
- These metrics describe model fit on the training test split. They do not represent prediction reliability for new songs in deployment.

---

## 9. Residual and Error Analysis

**Source:** `7.ML/7.8.model_evaluation/metrics/residual_statistics.json`
**Residual convention:** `actual − predicted` (positive = underprediction)
**Test rows:** 85,876

| Statistic | Value |
|---|---|
| Mean Residual | +4.857 (underprediction bias) |
| Residual Std Dev | 20.44 popularity points |
| Underprediction Rate | 67.8% |
| Overprediction Rate | 32.2% |

The model underpredicts roughly 2 out of 3 songs in the test set.

---

## 10. Artifact Packaging

**Canonical artifact root:** `artifacts/epic2/`

### Required Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| `full_inference_pipeline.joblib` | `pipeline/` | Serialized model + preprocessing pipeline |
| `input_schema.json` | `schemas/` | 18 canonical input field definitions |
| `output_schema.json` | `schemas/` | Prediction output field definitions |
| `selected_features.json` | `schemas/` | 31 selected feature names |
| `feature_names.json` | `schemas/` | 49 transformed model matrix column names |
| `feature_mapping.json` | `schemas/` | Maps raw features to transformed features |
| `example_input.json` | `examples/` | Canonical 18-field example input |
| `example_output.json` | `examples/` | Expected output for canonical example (46) |
| `model_version.json` | `metadata/` | Model ID, version, family |
| `package_version.json` | `metadata/` | Package version |
| `data_version.json` | `metadata/` | Data version |
| `artifact_manifest.json` | `metadata/` | Complete artifact inventory with SHA-256 hashes |

### SHAP Explainability Assets

Located under `7.ML/7.9.explainability/` (packaged as part of EPIC 2 handoff):

| Asset | Purpose |
|---|---|
| `shap_background_transformed.npy` | Background samples for TreeExplainer (1000 rows × 49 cols) |
| `shap_values_global.npy` | Global SHAP values (5000 samples × 49 features) |
| `shap_base_values.npy` | Base values array |
| `shap_feature_mapping.json` | Maps 18 raw → 49 transformed feature names |
| `shap_additivity_validation.json` | Validates: base + ΣSHAP ≈ prediction (100% pass) |

Full inventory: [feature_3_1_shap_asset_inventory.json](epic3/feature_3_1_artifact_validation/validation/feature_3_1_shap_asset_inventory.json) (16 assets total, 8 required, all found).

---

## 11. Artifact Validation Gate

Feature 3.1 performed a full validation pass across all artifacts:

**Final validation results:** [feature_3_1_final_validation_results.json](epic3/feature_3_1_artifact_validation/validation/feature_3_1_final_validation_results.json)

| Check | Result |
|---|---|
| All 18 required artifacts found | ✅ PASS |
| Model loads successfully | ✅ PASS |
| Zero refit calls | ✅ PASS (113 tests) |
| Input schema: 18 fields valid | ✅ PASS |
| Output schema: 8 fields valid | ✅ PASS |
| 31 selected features confirmed | ✅ PASS |
| 49 transformed features confirmed | ✅ PASS |
| SHAP assets: 8 required found | ✅ PASS |
| Example prediction: 46.421062 ± 0.001 | ✅ PASS |
| Model SHA-256 unchanged post-validation | ✅ PASS |

---

## 12. Input Contract

**Schema ID:** `HITRADAR-PREDICTION-INPUT-V1`

The API accepts 18 fields representing audio and metadata features. All fields are required. Out-of-range values generate a 422 validation error. Extra fields are accepted and ignored with a warning (`additionalProperties: allow`).

Field constraints (from `input_schema.json`):

| Field | Type | Range |
|---|---|---|
| duration_min | float | 0.0 – 120.0 |
| explicit | boolean | — |
| release_year | int | 1900 – 2100 |
| release_month | float | 1.0 – 12.0 |
| decade | int | 1900 – 2100 |
| release_precision | string | `day` \| `month` \| `year` |
| danceability | float | 0.0 – 1.0 |
| energy | float | 0.0 – 1.0 |
| key | int | 0 – 11 |
| loudness | float | −60.0 – 0.0 |
| mode | int | 0 – 1 |
| speechiness | float | 0.0 – 1.0 |
| acousticness | float | 0.0 – 1.0 |
| instrumentalness | float | 0.0 – 1.0 |
| liveness | float | 0.0 – 1.0 |
| valence | float | 0.0 – 1.0 |
| tempo | float | 0.0 – 300.0 |
| time_signature | float | — |

Full API reference: [API_DOCUMENTATION.md §7](API_DOCUMENTATION.md#7-post-predict)

---

## 13. Inference Pipeline

```
PredictRequest (18 fields)
    │
    ▼
Pydantic validation (FastAPI, 422 on failure)
    │
    ▼
PipelineLoader singleton (loads at backend startup)
    │
    ▼
HitRadarInferencePipeline.predict_popularity()
    │  1. Apply feature engineering (13 engineered features)
    │  2. Apply preprocessing (49-column model matrix)
    │  3. Run XGBoost.predict()
    │
    ▼
PredictResponse
    ├── prediction_raw: float  (may be outside [0,100])
    ├── prediction_clipped: float  (clipped to [0,100])
    └── prediction_display: int  (rounded for display)
```

The pipeline is thread-safe for concurrent predictions. Each prediction request is stateless.

---

## 14. Output Contract

**Schema ID:** `HITRADAR-PREDICTION-OUTPUT-V1`

| Field | Type | Description |
|---|---|---|
| `status` | string | `"SUCCESS"` or `"ERROR"` |
| `prediction_raw` | float | Raw model output (may be outside [0,100]) |
| `prediction_clipped` | float | Clipped to [0,100] |
| `prediction_display` | int | Rounded clipped value |
| `model_id` | string | `EXP24-XGB-FINAL-001` |
| `model_version` | string | `1.0.0` |
| `package_version` | string | Artifact package version |
| `warnings` | list[string] | Any warnings (e.g., extra fields ignored) |

Full API reference: [API_DOCUMENTATION.md §7](API_DOCUMENTATION.md#7-post-predict)

---

## 15. Explainability Architecture

```
PredictRequest (18 fields)
    │
    ▼
POST /explain  (FastAPI backend)
    │
    ▼
PipelineLoader.get_explainer()
    │  Creates shap.TreeExplainer(full_inference_pipeline.xgb_model)
    │  Uses shap_background_transformed.npy (1000 background samples)
    │  Cached in module-level singleton
    │
    ▼
shap.TreeExplainer.shap_values()
    │  Input: 49-column transformed matrix
    │  Output: 49 SHAP values
    │
    ▼
Map 49 SHAP values → 31 selected features
    │  (via shap_feature_mapping.json)
    │
    ▼
Select top 5 by absolute SHAP magnitude
    │
    ▼
ExplainResponse
    ├── base_value: float  (average model output)
    ├── shap_values: dict[str, float]  (31 entries)
    ├── top_features: list[TopFeature]  (top 5)
    └── prediction_display: int
```

**Frontend role:** Receives and renders the ExplainResponse. It does not compute SHAP values.

**Important:** SHAP values describe how the model weighed each input feature to arrive at its prediction. They do not establish causal relationships.

---

## 16. What-If Architecture

```
WhatIfRequest
├── base_features: PredictRequest (18 fields)
└── changed_features: dict[str, value]  (at least 1 key)
    │
    ▼
Merge base_features + changed_features
    │
    ▼
Run pipeline.predict_popularity() twice
    │  1. base_features → prediction_before
    │  2. merged → prediction_after
    │
    ▼
WhatIfResponse
    ├── prediction_before: PredictionShort
    ├── prediction_after: PredictionShort
    ├── delta: float  (after − before, clipped values)
    └── changes_applied: dict[str, value]
```

Validation: `changed_features` keys must be canonical field names; empty dict raises 422.

---

## 17. FastAPI Backend

### Module Structure

```
5.UNG_DUNG/5.1.backend_api/
├── api.py              ← FastAPI app + CORS + lifespan + routes
├── config.py           ← Settings dataclass + ARTIFACTS_PATH
├── pipeline_loader.py  ← Eager singleton load + runtime patches
├── runtime_patches.py  ← EPIC 2 compat: transformers + __main__ to_string
└── models/
    └── prediction.py   ← All Pydantic schemas
```

### Startup Behavior

The backend loads the model pipeline eagerly at startup (in the `lifespan` async context manager). The backend does not respond to `/predict`, `/explain`, `/what-if`, `/model-info`, or `/features` until `model_loaded == true`. `/health` always responds, returning `degraded` status while loading.

### CORS

CORS middleware is enabled to allow Streamlit (port 8501) to call the API from the browser. Origins and methods are configured in `api.py`.

### Error Handling

| Scenario | HTTP Code | Response |
|---|---|---|
| Validation failure (missing/out-of-range fields) | 422 | `HTTPValidationError` |
| Model not loaded | 503 | `ErrorResponse` with `error_code: MODEL_NOT_LOADED` |
| Internal error | 500 | `ErrorResponse` |

### Logging

Python `logging` module at `INFO` level. Request/response logging is configurable via environment.

---

## 18. API Endpoints

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for the full reference.

Summary:

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness + readiness |
| GET | `/model-info` | Metadata + metrics |
| GET | `/features` | 18 field definitions + 31 selected features |
| POST | `/predict` | Predict popularity |
| POST | `/explain` | Predict + SHAP attribution |
| POST | `/what-if` | Compare two scenarios |

---

## 19. Streamlit Frontend

### Navigation

Seven pages registered in `core/navigation.py`:

| Page | Backend Required |
|---|---|
| Home | No |
| Predict Popularity | Yes |
| SHAP Explanation | Yes |
| What-If Simulator | Yes |
| Music Trends | No |
| Model Info | Yes |
| Limitations & Responsible Use | No |

### API Client

`api/client.py` provides `HitRadarAPIClient` wrapping `httpx`. All HTTP calls go through this client. No direct model access.

### State Management

`core/session.py` provides `init_session_state()` and session helpers. Key cached values:
- `cached_features`: feature definitions (loaded once from `/features`)
- `current_prediction_input`: last prediction input (used by Explain + What-If)
- `current_prediction_result`: last prediction response
- `current_explanation`: last SHAP response
- `current_whatif`: last What-If response
- `backend_status`: `Connected` / `Degraded` / `Unavailable`

---

## 20. Dashboard Architecture

**Page:** `Music Trends` (4_Trends.py)
**Data sources:**

```
5.DATA/processed/ml_ready_dataset.csv
  └── release_year, audio features (danceability, energy, valence, tempo, etc.)
  └── Read by: @st.cache_data load_yearly_features()
  └── Aggregation: mean by release_year

7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv
  └── year, MAE, RMSE, R²
  └── Read by: @st.cache_data load_yearly_evaluation()
```

**Charts:**
- Songs per year (dataset distribution)
- Audio feature trends over decades (danceability, energy, valence, tempo, etc.)
- Correlation heatmap
- Prediction quality over time (MAE, RMSE, R² by year)

**Cache:** `@st.cache_data` decorators prevent re-aggregation on every rerun.

**Scope note:** The charts describe the project dataset (1900–2021). They are not a comprehensive representation of the global music industry.

---

## 21. Caching Strategy

| Layer | Mechanism | Scope |
|---|---|---|
| Backend SHAP explainer | Module-level singleton (`shap_explainer`) | Per-process; recreated on backend restart |
| Backend model | `PipelineLoader` singleton | Per-process; recreated on backend restart |
| Frontend feature definitions | `st.session_state.cached_features` | Per-user session |
| Frontend prediction results | `st.session_state.current_prediction_*` | Per-user session |
| Dashboard data | `@st.cache_data` decorators | Per-user session; invalidated on page refresh |

There is no distributed cache (Redis, Memcached). The frontend state lives in each user's Streamlit session.

---

## 22. End-to-End Testing

Feature 3.5 performed E2E validation across all endpoints:

**Evidence:** `Bao_cao_3/Báo cáo epic3/feature_3_5/validation/`

| Test | Source | Result |
|---|---|---|
| Canonical E2E fixture | `feature_3_5_canonical_e2e_fixture.json` | prediction_display: 46 |
| Health endpoint | `feature_3_5_health_e2e_validation.json` | healthy + model_loaded=true |
| Model info | `feature_3_5_model_info_e2e_validation.json` | model_id + metrics returned |
| Backend unavailable | `feature_3_5_backend_down_e2e.json` | Graceful degradation |
| Timeout handling | `feature_3_5_timeout_e2e_validation.json` | Timeout triggered correctly |

Example input/output used in E2E validation:
```json
// artifacts/epic2/examples/example_input.json
{
  "duration_min": 5.1767, "explicit": true, "release_year": 1992,
  "danceability": 0.785, "energy": 0.793, "key": 1, "loudness": -7.915,
  // ... all 18 fields
  "prediction_display": 46
}
```

---

## 23. Error and Negative Testing

| Scenario | Expected Behavior |
|---|---|
| Missing required field in `/predict` | HTTP 422 with field-level detail |
| Out-of-range value | HTTP 422 with range constraint |
| Unknown field in `changed_features` (what-if) | HTTP 422 |
| Empty `changed_features` | HTTP 422 |
| Model not loaded (any model endpoint) | HTTP 503 |
| Backend unreachable | Frontend shows "Backend Unavailable" |
| Local CSV not found (Music Trends) | Empty charts |

---

## 24. Performance Benchmark

**Source:** Feature 3.1 Phase 4 benchmark
**Original benchmark environment:** Local Python 3.13.7; `artifacts/epic2/`; `time.perf_counter_ns` timer. The later validated defense runtime used Python 3.13.14; no cross-environment performance improvement is inferred.
**Artifact:** `full_inference_pipeline.joblib` (4.0 MB)
**Validation:** [feature_3_1_benchmark_results.json](epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json)

| Operation | Mean | Median | Unit |
|---|---|---|---|
| Model load (cold start) | 928 ms | 700 ms | ms |
| First prediction (cold) | 22.2 ms | 21.0 ms | ms |
| Warm single inference | 15.6 ms | 14.3 ms | ms |

These numbers were measured in a local development environment with no network overhead. **No SLA is defined** for the HitRadar Pro demo application. Actual throughput depends on hardware, concurrent load, and deployment configuration.

---

## 25. Reliability and Startup Automation

Three launcher scripts in `scripts/`:

| Script | What it does |
|---|---|
| `run_all.py` | Validates artifacts → starts backend → polls `/health` until `model_loaded=true` → starts frontend → monitors both → Ctrl+C teardown |
| `run_backend.py` | Starts backend only; polls until ready; Ctrl+C teardown |
| `run_frontend.py` | Starts frontend only; warns if backend unreachable (does not fail); Ctrl+C teardown |

**Health polling:** `wait_for_health()` in `_common.py` polls `GET /health` at 0.5-second intervals with no fixed sleep. It waits up to 120 seconds (configurable via `BACKEND_HEALTH_TIMEOUT`).

**Port conflict handling:** Scripts refuse to start if the required port is occupied. They do not kill existing processes.

**Teardown:** Scripts only manage their own child processes. They never kill unrelated processes.

---

## 26. Offline Demo Architecture

Offline Demo Mode is activated when `OFFLINE_DEMO_MODE=true` or when the backend is unreachable.

**Behavior:**
- Predict page: displays precomputed validated example(s)
- SHAP Explanation: **not available** (requires live model)
- What-If Simulator: **not available** (requires live model)
- Music Trends: **available** (reads local CSV; no backend dependency)

**What offline mode is not:**
- A backup model
- A degraded version of the live model
- Suitable for evaluating arbitrary input variations

It is a **precomputed validated demonstration** used for presentations when the backend cannot run.

Full contract: [Bao_cao_3/Báo cáo epic3/feature_3_6/DEMO_RUNBOOK_FEATURE_3_6.md](Bao_cao_3/Báo%20cáo%20epic3/feature_3_6/DEMO_RUNBOOK_FEATURE_3_6.md)

---

## 27. Testing Strategy

### Unit Tests
Isolated tests of individual functions, classes, and modules. Example: Pydantic model parsing, pipeline input transformation, SHAP response parsing.

### Integration Tests
Tests of the API layer with a real (or mocked) model loader. Example: POST `/predict` → validate response structure.

### End-to-End Tests
Full request path from HTTP client to model artifact and back. Example: Feature 3.5 E2E validation against `example_input.json`.

### Smoke Tests
Lightweight checks that the system starts and responds on a clean environment. Example: `run_backend.py` startup + `/health` response.

> **Note:** Not all tests labeled "E2E" in the project are true end-to-end tests. See individual test files for actual scope.

---

## 28. Security and Operational Notes

**Scope:** Local academic/demo application. No production hardening applied.

- No authentication or authorization
- No rate limiting
- No API key management
- No TLS (HTTP only, localhost)
- No input sanitization beyond Pydantic schema validation
- Model artifacts are read-only at runtime

**Do not deploy this application as-is to production without a security review.**

---

## 29. Technical Limitations

Limitations are documented in full in [USER_MANUAL.md §10](USER_MANUAL.md#10-limitations--responsible-use) and summarized here for cross-reference:

| Category | Limitation | Source |
|---|---|---|
| MODEL | R² = 0.07 — model explains ~7% of popularity variance | `feature_3_1_model_metrics_validation.json` |
| PREDICTION | Prediction is a model estimate, not a guarantee | `6_Limitations.py` |
| SHAP | SHAP describes model behavior, not causation | `6_Limitations.py`, `openapi.json` |
| WHAT-IF | What-If compares model outputs, not real-world effects | `6_Limitations.py` |
| DATA | Project data: 1900–2021 Spotify-derived; not comprehensive | canonical dataset and split manifests |
| BIAS | Model may reflect training data biases; popularity ≠ musical quality | `6_Limitations.py` |
| OFFLINE | Offline mode uses precomputed scenarios, not live inference | `offline_demo_mode_contract.json` |
| PERFORMANCE | No SLA defined; benchmark is local development only | `feature_3_1_benchmark_results.json` |

---

## 30. Artifact and Evidence Index

| Document | Location |
|---|---|
| Model version metadata | `artifacts/epic2/metadata/model_version.json` |
| Artifact manifest (SHA-256) | `artifacts/epic2/metadata/artifact_manifest.json` |
| Full validation results | `epic3/feature_3_1_artifact_validation/validation/feature_3_1_final_validation_results.json` |
| Model metrics | `epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_metrics_validation.json` |
| SHAP asset inventory | `epic3/feature_3_1_artifact_validation/validation/feature_3_1_shap_asset_inventory.json` |
| Benchmark results | `epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json` |
| E2E fixtures | `Bao_cao_3/Báo cáo epic3/feature_3_5/validation/` |
| Demo runbook | `Bao_cao_3/Báo cáo epic3/feature_3_6/DEMO_RUNBOOK_FEATURE_3_6.md` |
| Feature 3.7 Phase 1 gate | `Bao_cao_3/Báo cáo epic3/feature_3_7/validation/feature_3_7_phase_1_gate.json` |
| Feature 3.7 Phase 2 gate | `Bao_cao_3/Báo cáo epic3/feature_3_7/validation/feature_3_7_phase_2_gate.json` |
| Feature 3.7 Phase 3 gate | `Bao_cao_3/Báo cáo epic3/feature_3_7/validation/feature_3_7_phase_3_gate.json` |
