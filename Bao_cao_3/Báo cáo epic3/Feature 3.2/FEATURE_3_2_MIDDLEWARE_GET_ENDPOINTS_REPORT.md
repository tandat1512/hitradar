# Feature 3.2 — Middleware & GET Endpoints Report
## Phase 3 — CORS, Request ID, Structured Logging, Error Handling, /health, /model-info, /features

**Feature:** 3.2 — FastAPI Backend
**Phase:** 3 / 6
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Router Structure

| Router | File | Endpoints |
|---|---|---|
| `health` | `app/api/routers/health.py` | GET /health |
| `model_info` | `app/api/routers/model_info.py` | GET /model-info, GET /features |
| `predict` | `app/api/routers/predict.py` | POST /predict |
| `explain` | `app/api/routers/explain.py` | POST /explain |
| `whatif` | `app/api/routers/whatif.py` | POST /what-if |

All routers tagged in OpenAPI: `["system"]` (health), `["model"]` (model-info, features), etc.

---

## 2. CORS Configuration

**Config source:** `app/core/config.py` — loaded from env var `ALLOWED_ORIGINS`

**Development origins (default):**
```
http://localhost:8501   ← Streamlit dev
http://127.0.0.1:8501
http://localhost:3000
```

**Override in production:** `ALLOWED_ORIGINS=https://your-domain.com`

**Methods:** `["GET", "POST"]`
**Headers:** `["Accept", "Accept-Language", "Authorization", "Content-Type", "X-Request-ID"]`
**Credentials:** `True` (safe because origins are specific, not `*`)

**Violation check:**
```
Wildcard (*):              NO  ✅
Wildcard + Credentials:   NO  ✅
```

---

## 3. Request ID Middleware

**Header:** `X-Request-ID`

**Behavior:**
- Accept from client if present, valid format (alphanumeric, dash, underscore, ≤64 chars)
- Otherwise generate UUID4
- Stored in `request.state.request_id`
- Returned in response `X-Request-ID` header
- Present in all structured log lines

**Validation:**
```
null input  → generates UUID4         ✅
valid ID    → preserved as-is         ✅
too long    → truncated to ≤64 chars  ✅
control chars → rejected, new UUID    ✅
```

---

## 4. Structured Logging

**Logger:** `app.middleware.request`
**Format:** Single-line JSON per request

**Fields per log line:**
```json
{"event":"request","request_id":"uuid","method":"GET","path":"/health","status":200,"duration_ms":1.87,"client":"testclient","user_agent":"...","redacted_query":{}}
```

**Sensitive header redaction list:**
```
authorization, proxy-authorization, cookie, set-cookie,
x-api-key, x-auth-token, x-csrf-token
```

**NOT logged by default:**
- Full audio feature payload
- Model object / artifact bytes
- Stack trace (server-side only)

---

## 5. Centralized Error Handling

**4 exception handlers registered on the app:**

| Handler | Exception | HTTP Status | Error Code |
|---|---|---|---|
| `BackendError` | `BackendError` | `exc.status_code` | `exc.code` |
| `ValidationError` | `RequestValidationError` | 422 | `VALIDATION_ERROR` |
| `HTTPException` | `StarletteHTTPException` | `exc.status_code` | `HTTP_{code}` |
| `Unexpected` | `Exception` | 500 | `INTERNAL_ERROR` |

**Error response contract:**
```json
{
  "error": { "code": "...", "message": "...", "details": [] },
  "request_id": "uuid",
  "timestamp": "2026-08-06T..."
}
```

**Traceback exposure:** Never exposed to API clients. Full traceback logged server-side only.

---

## 6. GET /health

**Path:** `GET /health`
**Tags:** `["system"]`

**Response fields:**
- `status`: `"healthy"` | `"degraded"` | `"unavailable"`
- `service_name`: from `config.APP_NAME`
- `api_version`: from `config.APP_VERSION`
- `model_loaded`: bool
- `model_ready`: bool (alias for model_loaded)
- `explain_service_available`: `true`
- `what_if_available`: `true`
- `model_version`: from `PipelineLoader.get_model_version()` or `null`
- `timestamp`: UTC ISO format

**Liveness vs Readiness:**
- App started, pipeline loading → `"degraded"`
- App not started → `"unavailable"`
- Pipeline loaded → `"healthy"`

**Performance:** Does NOT run full model prediction. Only checks singleton state.

---

## 7. GET /model-info

**Path:** `GET /model-info`
**Tags:** `["model"]`
**Requires:** model loaded (503 if not)

**Response fields:**
- `model_id`: `"EXP24-XGB-FINAL-001"`
- `model_version`: `"1.0.0"`
- `model_family`: `"XGBoost"`
- `package_version`: `"2.7.0"`
- `data_version`: `"v1.0"`
- `feature_set`: `"FS23-SELECTED"`
- `training_date`: from metadata
- `metrics`: MAE, RMSE, R² from `champion_test_metrics.json`
- `timestamp`: UTC ISO

**Internal path exposure:** NONE. No `<PROJECT_ROOT>`, no `.joblib`, no `/artifacts/` paths.

---

## 8. GET /features

**Path:** `GET /features`
**Tags:** `["model"]`
**Requires:** model loaded (503 if not)

**Response fields:**
- `canonical_fields`: 18 `FieldDescriptor` objects
- `selected_features`: list of 31 feature names
- `total_input_fields`: 18
- `total_selected_features`: 31
- `timestamp`: UTC ISO

**FieldDescriptor per field:**
```json
{"name":"danceability","position":7,"data_type":"float","required":true,
 "minimum":0.0,"maximum":1.0,"allowed_categories":null,"default_policy":"PIPELINE_IMPUTE"}
```

**Internal path exposure:** NONE.

---

## 9. Dependency Injection

Services are injected via FastAPI `Depends()` or direct constructor:

```python
def _model_service() -> ModelService:
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(status_code=503, ...)
    return ModelService(pl)
```

Tests override `_model_service` via FastAPI dependency override mechanism.

---

## 10. Startup Failure Policy

**Current policy:** `degraded` — app starts even if model unavailable.

- GET /health → 200 with `status: "unavailable"`
- GET /model-info → 503
- GET /features → 503
- POST /predict → 503

This is controlled by `FAIL_STARTUP_IF_MODEL_UNAVAILABLE` env var (default: `false`).

---

## 11. HTTP Status Code Policy

| Status | When |
|---|---|
| 200 | Successful GET |
| 422 | Request validation failed |
| 500 | Unexpected internal error |
| 503 | Model not loaded / service unavailable |

---

## 12. Tests Phase 3

| Metric | Value |
|---|---|
| Collected | 33 |
| Passed | **33** |
| Failed | 0 |
| Errors | 0 |

**33/33 tests PASS.**

Test classes:
- `TestCORSAllowedOrigin`, `TestCORSPreflight` — 3 tests
- `TestRequestIDGenerated`, `TestRequestIDPropagated` — 4 tests
- `TestLoggingStructure`, `TestLoggingRedaction` — 2 tests
- `TestValidationErrorHandler`, `TestServiceErrorHandler` — 2 tests
- `TestUnexpectedErrorHandler`, `TestErrorResponseNoTraceback` — 2 tests
- `TestHealthHealthy`, `TestHealthUnavailable` — 4 tests
- `TestModelInfo`, `TestModelInfoConsistency` — 3 tests
- `TestFeatures`, `TestFeaturesRawContract` — 5 tests
- `TestDependencyOverride` — 1 test

---

## 13. Validation Artifacts

| Artifact | Status |
|---|---|
| feature_3_2_phase_3_prerequisite_validation.json | PASS |
| feature_3_2_cors_validation.json | PASS |
| feature_3_2_request_id_validation.json | PASS |
| feature_3_2_logging_validation.json | PASS |
| feature_3_2_error_handling_validation.json | PASS |
| feature_3_2_health_endpoint_validation.json | PASS |
| feature_3_2_model_info_endpoint_validation.json | PASS |
| feature_3_2_features_endpoint_validation.json | PASS |

**8/8 validation artifacts: PASS.**

---

## 14. Hard Rules Compliance

| Rule | Status |
|---|---|
| No train/refit | ✅ |
| CORS wildcard + credentials | ❌ (fixed) |
| No full payload logging | ✅ |
| No traceback in response | ✅ |
| No internal paths exposed | ✅ |
| No hardcoded production origins | ✅ |

---

## 15. Warnings

| ID | Severity | Detail |
|---|---|---|
| W1 | INFO | sklearn version mismatch: pipeline pickled 1.9.0 vs runtime 1.8.0 |
| W2 | INFO | httpx/starlette testclient deprecation — recommend `httpx2` |

---

## 16. Blockers

None.

---

## 17. Phase 3 Gate

| Criterion | Status |
|---|---|
| CORS valid | ✅ |
| CORS wildcard + credentials violation | **NO** ✅ |
| Request ID middleware | ✅ |
| Structured logging | ✅ |
| Log redaction | ✅ |
| Centralized error handling | ✅ |
| Traceback NOT exposed | ✅ |
| GET /health | ✅ |
| GET /model-info | ✅ |
| GET /features | ✅ |
| Dependency injection | ✅ |
| Training executed | NO ✅ |
| Refit executed | NO ✅ |
| Tests 33/33 PASS | ✅ |
| Blockers | 0 ✅ |

**Phase 3 Gate: PASS — MAY BEGIN Phase 4**
