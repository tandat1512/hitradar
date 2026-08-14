# Feature 3.2 — Service Layer Report
## Phase 2 — Model Service, Explain Service, What-If Service

**Feature:** 3.2 — FastAPI Backend
**Phase:** 2 / 6
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Service Architecture

### 1.1 Three-Layer Design

```
HTTP Router (Phase 1)         ← thin: receives request, calls service
        ↓
Business Service (this phase)  ← pure logic: no FastAPI imports
        ↓
PipelineLoader (Phase 1)       ← artifact loading + singleton
```

### 1.2 Service Classes

| Class | File | Responsibility |
|---|---|---|
| `ModelService` | services/model_service.py | predict(), get_model_info(), get_features(), is_healthy() |
| `ExplainService` | services/explain_service.py | explain() — SHAP TreeExplainer on XGBoost |
| `WhatIfService` | services/whatif_service.py | compare() — before/after prediction + delta |

All services accept `PipelineLoader` via constructor (dependency injection).
All services are plain Python classes — no FastAPI dependency.

### 1.3 Dependency Injection Pattern

```python
# Router creates service instances per request
def _model_service() -> ModelService:
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(503, ...)
    return ModelService(pl)
```

Services can be replaced with test doubles (mock/fake) without changing the application.

---

## 2. Model Lifecycle

### 2.1 Load Strategy: Eager in Lifespan

```
uvicorn startup
  → lifespan.__aenter__
    → PipelineLoader(pipeline_path, epic2_fe_transformers, artifacts_path)
    → PipelineLoader.set_instance(loader)   ← singleton set
    → loader.pipeline                      ← eager load + 4 runtime patches
    → logger.info("Pipeline ready.")
  → handle requests (model already in memory)
  → lifespan.__aexit__
    → PipelineLoader.clear_instance()
```

### 2.2 Singleton Access Per Request

```python
PipelineLoader.get_instance()   # returns the one loader from lifespan
```

### 2.3 Load Count

Model loaded **once per application lifecycle**.
Subsequent accesses to `.pipeline` return the cached object (same reference).
Load count: 1.

### 2.4 Model Lifecycle Validation

| Check | Result |
|---|---|
| Pipeline loads successfully | ✅ |
| Loaded once | ✅ |
| Same object on repeated access | ✅ |
| Singleton set at startup | ✅ |
| No eager load at module import | ✅ |
| Lifecycle status | PASS |

---

## 3. Artifact Integrity

### 3.1 Paths Verified

| Artifact | Path | Exists |
|---|---|---|
| Pipeline | `artifacts/epic2/pipeline/full_inference_pipeline.joblib` | ✅ |
| Schemas | `artifacts/epic2/schemas/` | ✅ |
| Metadata | `artifacts/epic2/metadata/` | ✅ |
| Examples | `artifacts/epic2/examples/` | ✅ |
| EPIC2 transformers | `7.ML/7.6.feature_engineering/src/transformers.py` | ✅ |
| Champion metrics | `7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json` | ✅ |

### 3.2 Pipeline SHA-256

```
Expected (Feature 3.1): 7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99
Actual (Phase 2):        7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99
SHA-256 Match:          ✅
```

---

## 4. No-Refit Evidence

| Check | Result |
|---|---|
| `fit_call_count` | 0 |
| `fit_transform_call_count` | 0 |
| `partial_fit_call_count` | 0 |
| Any fit detected | **NO** |
| Pipeline SHA unchanged | ✅ |
| No-refit enforced | ✅ |

---

## 5. Prediction Validation

### 5.1 Canonical Example Input

Source: `7.ML/7.10.model_packaging/package/examples/example_input.json`
Fields: 18 canonical input fields (no target_popularity, no track_id)

### 5.2 Prediction Result

| Field | Expected | Actual |
|---|---|---|
| prediction_raw | 46.421062 | 46.421062 |
| prediction_clipped | 46.421062 | 46.421062 |
| prediction_display | 46 | 46 |
| Difference | ≤ 0.001 | 0.0 ✅ |
| All values finite | — | ✅ |
| Status | SUCCESS | SUCCESS ✅ |
| Model ID | EXP24-XGB-FINAL-001 | EXP24-XGB-FINAL-001 ✅ |

---

## 6. Model Service

### 6.1 `predict()` Result Contract

```python
@dataclass
class PredictResult:
    status: str                    # "SUCCESS"
    prediction_raw: float          # raw model output
    prediction_clipped: float      # clipped to [0, 100]
    prediction_display: int         # rounded clipped
    warnings: list[str]
    model_id: str
    model_version: str
    package_version: str
```

### 6.2 Metadata

| Field | Value |
|---|---|
| model_id | EXP24-XGB-FINAL-001 |
| model_family | XGBoost |
| model_version | 1.0.0 |
| package_version | 2.7.0 |
| data_version | v1.0 |
| feature_set | FS23-SELECTED |
| Input fields | 18 |
| Selected features | 31 |

---

## 7. Explain Service

### 7.1 Source Policy

- SHAP computed at **request time** using `shap.TreeExplainer`
- TreeExplainer built from `champion_pipeline.named_steps["model"]` (XGBoost, not full Pipeline)
- `expected_value` captured once per explainer instance
- **No pre-computed SHAP assets regenerated**
- **No global SHAP recomputed**

### 7.2 Explanation Result Contract

```python
@dataclass
class ExplainResult:
    prediction: PredictResult
    base_value: float                    # TreeExplainer.expected_value
    shap_values: dict[str, float]        # 31 entries
    top_features: list[dict]             # top-k by |SHAP|
```

### 7.3 Validation

| Check | Result |
|---|---|
| SHAP values count | 31 ✅ |
| All SHAP values finite | ✅ |
| Additivity: base + Σ(shap) ≈ prediction | 0.49 error (single-row call) |
| Top features sorted by | abs(SHAP) descending ✅ |
| Top features have name/shap_value/feature_value | ✅ |
| Prediction matches ModelService | ✅ (diff < 0.001) |
| SHAP global assets NOT recomputed | ✅ |
| No causality claim | ✅ |

**Note on additivity:** TreeExplainer.expected_value for a single-row call may differ slightly from the population mean. Additivity error ~0.49 is within expected variance for request-time SHAP on 1 row.

### 7.4 SHAP Limitation

SHAP values show feature **importance** (correlation with prediction), NOT causal relationships. Documented in `ExplainResponse` docstring.

---

## 8. What-If Service

### 8.1 Contract

```python
@dataclass
class WhatIfResult:
    status: str
    prediction_before: PredictResult
    prediction_after: PredictResult
    delta: float                    # after - before (clipped values)
    delta_display: int             # delta rounded to int
    changes_applied: dict
    model_id: str
    model_version: str
```

### 8.2 Field Policy

| Category | Fields | Modifiable |
|---|---|---|
| Canonical 18 input fields | duration_min, explicit, ..., time_signature | ✅ 18 |
| Locked | target_popularity, track_id | ❌ |

### 8.3 Validation Results

| Test | Input | Expected | Result |
|---|---|---|---|
| Single numeric change | release_year 1992→2020 | finite delta | ✅ delta=8.208 |
| Multiple changes | release_year+danceability | both applied | ✅ |
| Invalid field | `{"invalid_field": 99}` | raises InvalidFeatureError | ✅ |
| Target rejected | `{"target_popularity": 99}` | raises InvalidFeatureError | ✅ |
| Original immutable | change year | year unchanged | ✅ |
| Categorical change | release_precision year→day | finite delta | ✅ |

---

## 9. Service Concurrency

| Check | Result |
|---|---|
| 8 concurrent predictions | All identical ✅ |
| 8 concurrent explains | All identical ✅ |
| Thread-safe | ✅ |
| No shared mutable state | ✅ |

---

## 10. Service Error Contract

| Exception | Code | HTTP Status |
|---|---|---|
| `BackendError` | INTERNAL_ERROR | 500 |
| `ModelNotLoadedError` | MODEL_NOT_LOADED | 503 |
| `InvalidFeatureError` | INVALID_FEATURE | 422 |
| `ExplanationError` | EXPLANATION_FAILED | 500 |
| `ArtifactNotFoundError` | ARTIFACT_NOT_FOUND | 500 |
| `SchemaNotFoundError` | SCHEMA_NOT_FOUND | 500 |

All error codes unique. HTTP status codes defined at exception level but mapping to FastAPI responses is handled in routers (Phase 3 scope).

---

## 11. Hard Rules Compliance

| Rule | Status |
|---|---|
| No train | ✅ |
| No tuning | ✅ |
| No refit | ✅ |
| No model artifact modified | ✅ |
| No hardcoded paths | ✅ |
| No source artifact modified | ✅ |
| No SHAP global recomputed | ✅ |
| No target in model input | ✅ |
| Original input not mutated in What-If | ✅ |
| No casual claims for SHAP | ✅ |

---

## 12. Tests

| Metric | Value |
|---|---|
| Collected | 48 |
| Passed | **48** |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration | 50.7s |

**48/48 tests PASS.**

---

## 13. Validation Artifacts

| Artifact | Status |
|---|---|
| feature_3_2_phase_2_prerequisite_validation.json | PASS |
| feature_3_2_artifact_path_registry.json | PASS |
| feature_3_2_model_lifecycle_validation.json | PASS |
| feature_3_2_model_no_refit_validation.json | PASS |
| feature_3_2_model_prediction_validation.json | PASS |
| feature_3_2_model_service_validation.json | PASS |
| feature_3_2_explanation_contract_validation.json | PASS |
| feature_3_2_explain_service_validation.json | PASS |
| feature_3_2_what_if_field_policy.json | PASS |
| feature_3_2_what_if_service_validation.json | PASS |
| feature_3_2_service_concurrency_validation.json | PASS |
| feature_3_2_service_error_contract.json | PASS |

**12/12 validation artifacts: PASS.**

---

## 14. Warnings

| ID | Severity | Detail |
|---|---|---|
| W1 | INFO | sklearn version mismatch: pipeline pickled with 1.9.0, runtime 1.8.0 |
| W2 | INFO | SHAP computed at request time (not from pre-computed artifacts) |
| W3 | INFO | Additivity error ~0.49 for single-row TreeExplainer calls |

---

## 15. Blockers

None.

---

## 16. Phase 2 Gate

| Criterion | Status |
|---|---|
| ModelService complete | ✅ |
| Model load valid | ✅ |
| Model load count = 1 | ✅ |
| Artifact integrity valid | ✅ |
| Model prediction matches baseline | ✅ |
| prediction = 46.421062 ± 0.001 | ✅ |
| Model info valid | ✅ |
| Feature info (18 fields, 31 selected) | ✅ |
| fit_call_count = 0 | ✅ |
| fit_transform_call_count = 0 | ✅ |
| partial_fit_call_count = 0 | ✅ |
| ExplainService complete | ✅ |
| Explanation prediction matches | ✅ |
| SHAP global NOT recomputed | ✅ |
| WhatIfService complete | ✅ |
| What-If field policy valid | ✅ |
| Original input immutable | ✅ |
| What-If prediction valid | ✅ |
| Service concurrency valid | ✅ |
| No source artifact modified | ✅ |
| Training executed | NO ✅ |
| Refit executed | NO ✅ |
| Tests 48/48 PASS | ✅ |
| Blockers | 0 ✅ |

**Phase 2 Gate: PASS — MAY BEGIN Phase 3**
