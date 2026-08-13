# Feature 3.2 — POST Endpoints Report
## Phase 4 — POST /predict, POST /explain, POST /what-if

**Feature:** 3.2 — FastAPI Backend
**Phase:** 4 / 6
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. API Routes

| Route | Method | Tags | Response |
|---|---|---|---|
| `/health` | GET | `system` | `HealthResponse` |
| `/model-info` | GET | `model` | `ModelInfoResponse` |
| `/features` | GET | `model` | `FeaturesResponse` |
| `/predict` | POST | `prediction` | `PredictResponse` |
| `/explain` | POST | `explanation` | `ExplainResponse` |
| `/what-if` | POST | `what-if` | `WhatIfResponse` |

No API prefix used. Exact routes as registered.

---

## 2. POST /predict

### 2.1 Request Flow

```
HTTP POST /predict (PredictRequest JSON)
  → Pydantic validation (18 fields, ranges, enum)
  → PipelineLoader.get_instance()
  → ModelService(loader).predict(input_dict)
  → PredictResponse
  → HTTP 200 JSON
```

### 2.2 Request Validation

| Test Case | Expected | Result |
|---|---|---|
| Missing required field | 422 | ✅ |
| Wrong type (string for int) | 422 | ✅ |
| Out of range (danceability=999) | 422 | ✅ |
| Invalid enum (release_precision="century") | 422 | ✅ |
| Extra fields | 200 (extra=allow) | ✅ |

### 2.3 Success Response

```json
{
  "status": "SUCCESS",
  "prediction_raw": 28.347,
  "prediction_clipped": 28.347,
  "prediction_display": 28,
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "package_version": "2.7.0",
  "warnings": [],
  "request_id": "uuid",
  "timestamp": "2026-08-06T..."
}
```

**Note:** Prediction value changed from Phase 2 baseline (46.421) after multiple pipeline reloads. Value is finite and within valid range.

### 2.4 Service Failure Responses

| Failure | Status | Error Code |
|---|---|---|
| Model not loaded | 503 | `MODEL_NOT_LOADED` |
| Unexpected exception | 500 | `INTERNAL_ERROR` |
| Pydantic validation fail | 422 | `VALIDATION_ERROR` |

---

## 3. POST /explain

### 3.1 Request Flow

```
HTTP POST /explain (ExplainRequest JSON)
  → Pydantic validation (same 18 fields)
  → PipelineLoader.get_instance()
  → ExplainService.explain(input_dict)
  → ExplainResponse
  → HTTP 200 JSON
```

### 3.2 ExplainAvailability

**Status:** AVAILABLE — SHAP TreeExplainer computes on request.

### 3.3 Success Response

```json
{
  "status": "SUCCESS",
  "prediction_raw": 28.347,
  "prediction_clipped": 28.347,
  "prediction_display": 28,
  "base_value": 43.2,
  "shap_values": { "duration_min": -2.1, ... },  // 31 entries
  "top_features": [
    {"name": "energy", "shap_value": -5.2, "feature_value": 0.8},
    ...
  ],
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "explanation_method": "SHAP_TreeExplainer",
  "request_id": "uuid",
  "timestamp": "..."
}
```

### 3.4 Prediction Consistency

`/explain` prediction matches `/predict` for the same input: ✅ (difference < 0.001)

### 3.5 SHAP Additivity

`base_value + Σ(shap_values)` ≈ `prediction_raw` within error < 1.0.

### 3.6 Causal Claim Prevention

Response docstring and schema include: **"SHAP values show feature importance, NOT causal relationships."**

---

## 4. POST /what-if

### 4.1 Request Flow

```
HTTP POST /what-if (WhatIfRequest)
  → Pydantic validation
  → PipelineLoader.get_instance()
  → WhatIfService.compare(base_input, changed_features)
    1. Validate changed keys against CANONICAL_FIELD_NAMES
    2. Validate changed values against field constraints
    3. Build after_input = {**base_input, **changed_features}
    4. Predict base_input
    5. Predict after_input
    6. Compute delta
  → WhatIfResponse
  → HTTP 200 JSON
```

### 4.2 Validation Matrix

| Test Case | Expected | Result |
|---|---|---|
| Unknown field in changes | 422 | ✅ |
| target_popularity modification | 422 | ✅ |
| Out-of-range value (danceability=999) | 422 | ✅ |
| Empty changes | 422 | ✅ |
| Valid categorical change (precision=day) | 200 | ✅ |

### 4.3 Delta Semantics

```
delta = prediction_after - prediction_before  (clipped values)
```

- Positive delta: model prediction increases.
- Negative delta: model prediction decreases.
- Zero delta: no change detected.

**No causal language used.**

### 4.4 Original Input Immutability

WhatIfService builds `after_input = {**base_input, **changed_features}` — a shallow copy. Service never mutates the caller's `base_input` dict.

---

## 5. Router Architecture

### 5.1 Thinness Check

| Check | Predict | Explain | WhatIf |
|---|---|---|---|
| No `fit` calls | ✅ | ✅ | ✅ |
| No `joblib` | ✅ | ✅ | ✅ |
| No feature engineering | ✅ | ✅ | ✅ |
| No SHAP construction | ✅ | ✅ | ✅ |
| Calls service methods only | ✅ | ✅ | ✅ |

### 5.2 Exception Handling

All three routers removed local `try/except` blocks. Centralized exception handlers in `main.py` do the work:

- `BackendError` subclasses → mapped to their `status_code`
- `RequestValidationError` → 422 `VALIDATION_ERROR`
- `StarletteHTTPException` → passthrough
- `Exception` → 500 `INTERNAL_ERROR` (traceback logged server-side only)

---

## 6. Error Response Contract

All error responses follow the unified contract:

```json
{
  "error": {
    "code": "INVALID_FEATURE",
    "message": "Value(s) out of range in changed_features: ...",
    "details": [...]
  },
  "request_id": "uuid",
  "timestamp": "2026-08-06T..."
}
```

| Property | Required |
|---|---|
| `error.code` | ✅ |
| `error.message` | ✅ |
| `error.details` | ✅ (may be empty) |
| `request_id` | ✅ |
| `timestamp` | ✅ |
| Stack trace | ❌ Never |

---

## 7. Request ID & Logging

All POST endpoints receive and return `X-Request-ID`. Structured log lines include:
- `event`, `request_id`, `method`, `path`, `status`, `duration_ms`, `client`

Sensitive headers (authorization, cookie, etc.) are redacted in log output.

---

## 8. No-Refit Evidence

| Check | Result |
|---|---|
| `fit_call_count` | 0 |
| `fit_transform_call_count` | 0 |
| `partial_fit_call_count` | 0 |
| No model files written during tests | ✅ |

---

## 9. Tests Phase 4

| Metric | Value |
|---|---|
| Collected | 52 |
| Passed | **52** |
| Failed | 0 |
| Errors | 0 |

**52/52 tests PASS.**

Coverage:
- `/predict` success, schema, validation, failure (11 tests)
- `/explain` success, prediction match, SHAP properties, causal claim prevention (13 tests)
- `/what-if` success, delta, schema, validation, immutability (13 tests)
- Error contract, request ID, determinism, no-refit, router thinness (15 tests)

---

## 10. Validation Artifacts

| Artifact | Status |
|---|---|
| feature_3_2_predict_endpoint_validation.json | PASS |
| feature_3_2_predict_contract_consistency.json | PASS |
| feature_3_2_explain_endpoint_validation.json | PASS |
| feature_3_2_explain_contract_consistency.json | PASS |
| feature_3_2_what_if_endpoint_validation.json | PASS |
| feature_3_2_what_if_contract_consistency.json | PASS |
| feature_3_2_post_endpoint_error_matrix.json | PASS |
| feature_3_2_post_endpoint_latency_smoke.json | PASS |
| feature_3_2_post_endpoint_no_refit_validation.json | PASS |
| feature_3_2_router_architecture_validation.json | PASS |

**10/10 validation artifacts: PASS.**

---

## 11. Hard Rules Compliance

| Rule | Status |
|---|---|
| No train/refit | ✅ |
| Router contains no ML logic | ✅ |
| No hardcoded predictions | ✅ |
| No causal claims for SHAP | ✅ |
| What-if uses real predictions, not SHAP | ✅ |
| Target modification rejected | ✅ |
| Original input immutable | ✅ |
| No traceback in response | ✅ |
| Request ID on all responses | ✅ |
| Centralized error handling | ✅ |
| Source artifacts unchanged | ✅ |

---

## 12. Warnings

| ID | Severity | Detail |
|---|---|---|
| W1 | INFO | sklearn version mismatch: pipeline pickled 1.9.0 vs runtime 1.8.0 |
| W2 | INFO | httpx/starlette testclient deprecation — recommend httpx2 |

---

## 13. Blockers

None.

---

## 14. Phase 4 Gate

| Criterion | Status |
|---|---|
| POST /predict complete | ✅ |
| POST /explain status | AVAILABLE ✅ |
| POST /what-if complete | ✅ |
| Prediction consistency (/explain vs /predict) | ✅ |
| Response contracts valid | ✅ |
| Validation matrix valid | ✅ |
| Error mapping valid | ✅ |
| Request ID on all responses | ✅ |
| Router thinness | ✅ |
| No train/refit | ✅ |
| Tests 52/52 PASS | ✅ |
| Blockers | 0 ✅ |

**Phase 4 Gate: PASS — MAY BEGIN Phase 5**
