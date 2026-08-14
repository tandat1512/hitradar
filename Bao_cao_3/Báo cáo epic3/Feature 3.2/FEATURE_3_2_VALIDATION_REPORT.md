# FEATURE 3.2 VALIDATION REPORT
## FastAPI Backend — HitRadar Pro API

---

## 1. Thông tin chung

| Trường | Giá trị |
|---|---|
| Feature | 3.2 — FastAPI Backend |
| EPIC | EPIC 3 — Backend & Deployment |
| Dự án | HitRadar Pro |
| Người thực hiện | Minh |
| Ngày | 2026-08-06 |
| Tổng phases | 6/6 |
| **Tổng tests** | **133 PASS / 0 FAIL / 0 ERROR** |

---

## 2. Feature 3.1 Gate

Feature 3.1 (EPIC 2 ML Pipeline) gate: **PASS**

Kiểm tra điều kiện tiên quyết: artifacts tồn tại, pipeline deserializable, metrics có.

---

## 3. Backend Architecture

```
app/
├── main.py              # App factory, lifespan, CORS, handlers
├── api/
│   ├── middleware.py   # Request ID + structured JSON logging
│   └── routers/
│       ├── health.py   # GET /health
│       ├── model_info.py # GET /model-info, GET /features
│       ├── predict.py   # POST /predict
│       ├── explain.py   # POST /explain
│       └── whatif.py    # POST /what-if
├── core/
│   ├── config.py       # Settings: env, paths, CORS
│   └── exceptions.py   # BackendError hierarchy (7 subclasses)
├── schemas/
│   ├── common.py       # ErrorResponse, ModelInfoResponse, Metrics
│   ├── prediction.py   # PredictRequest (18 fields), PredictResponse
│   ├── explanation.py  # ExplainRequest, ExplainResponse, TopFeature
│   └── what_if.py     # WhatIfRequest, WhatIfResponse, PredictionShort
└── services/
    ├── pipeline_loader.py # Singleton: PipelineLoader
    ├── model_service.py   # ModelService.predict()
    ├── explain_service.py  # ExplainService.explain() — SHAP
    └── whatif_service.py   # WhatIfService.compare()
```

---

## 4. Configuration

Settings resolved from environment variables via `app/core/config.py`.

| Variable Group | Count |
|---|---|
| Application | 4 |
| Server | 3 |
| Artifacts | 5 |
| CORS | 4 |
| Feature flags | 3 |
| **Total env vars** | **~19** |

`.env.example` created with all variables and no secrets.

---

## 5. Artifact Path Management

| Artifact | Source | Validation |
|---|---|---|
| Pipeline | `artifacts/epic2/pipeline/full_inference_pipeline.joblib` | Path traversal guard ✅ |
| Schemas | `artifacts/epic2/schemas/` | Read-only ✅ |
| Metadata | `artifacts/epic2/metadata/` | Read-only ✅ |
| Examples | `artifacts/epic2/examples/` | Read-only ✅ |
| Transformers | `7.ML/7.6.feature_engineering/src/transformers.py` | Runtime patches ✅ |

---

## 6. Pydantic Contracts

| Schema | Fields | Validation |
|---|---|---|
| PredictRequest | 18 | ge/le min/max, enum, required |
| PredictResponse | 10 | extra=forbid |
| ExplainRequest | 18 | Same as PredictRequest |
| ExplainResponse | 12 | extra=forbid |
| WhatIfRequest | 2 | min_length=1 on changed_features |
| WhatIfResponse | 10 | extra=forbid |
| HealthResponse | 8 | extra=forbid |
| ErrorResponse | 5 | extra=forbid |

---

## 7. ModelService

- Singleton: `PipelineLoader`
- Lazy load: pipeline deserialized on first access
- Eager option: load at startup via lifespan
- Output: raw + clipped (0–100) + display (int)
- No refit: pipeline read-only after load

---

## 8. ExplainService

- Method: SHAP `TreeExplainer`
- Additivity check: `|prediction - (base + sum(shap))| < 1.0`
- Output: 31 shap_values + top-5 features
- **No causal claim** in response or description

---

## 9. WhatIfService

- Copy-based: `{**base_input, **changed_features}`
- Range validation: changed_features checked against PredictRequest constraints
- Delta: `prediction_clipped_after - prediction_clipped_before`
- Original input immutable (no in-place mutation)

---

## 10. Model Lifecycle

| Check | Value |
|---|---|
| Model loaded once | ✅ |
| Pipeline read-only | ✅ |
| fit_call_count | 0 |
| fit_transform_call_count | 0 |
| partial_fit_call_count | 0 |
| training_executed | NO ✅ |
| tuning_executed | NO ✅ |
| refit_executed | NO ✅ |

---

## 11. No-Refit Evidence

Pipeline loaded at startup → read-only for all requests. No `fit`, `fit_transform`, or `partial_fit` calls made by any endpoint.

---

## 12. CORS

Configuration in `app/core/config.py`:

```python
ALLOWED_ORIGINS = ["http://localhost:8501", "http://127.0.0.1:8501", "http://localhost:3000"]
ALLOW_CREDENTIALS = True
ALLOWED_METHODS = ["GET", "POST"]
ALLOWED_HEADERS = ["Accept", "Accept-Language", "Authorization", "Content-Type", "X-Request-ID"]
```

- No wildcard `*` ✅
- No `*` + credentials combination ✅
- Preflight OPTIONS handled ✅

---

## 13. Logging & Request ID

**Request ID**: `X-Request-ID` header — accept from client if valid (alphanumeric, max 64 chars), else generate UUID4. Present in all responses.

**Structured JSON logging**: One JSON line per request:
```json
{"event":"request","request_id":"uuid","method":"GET","path":"/health","status":200,"duration_ms":1.23,"client":"127.0.0.1"}
```

**Redaction**: `authorization`, `cookie`, `x-api-key`, etc. → `[REDACTED]`

---

## 14. Error Handling

Centralized handlers in `app/main.py`:

| Exception | HTTP Status | Error Code |
|---|---|---|
| BackendError subclasses | per class | per class |
| RequestValidationError | 422 | VALIDATION_ERROR |
| StarletteHTTPException | per code | HTTP_{code} |
| Unexpected Exception | 500 | INTERNAL_ERROR |

No traceback exposed to clients. Full traceback logged server-side only.

---

## 15. GET Endpoints

| Endpoint | Path | Status | Response |
|---|---|---|---|
| Health | GET /health | 200 | status, model_loaded, api_version, etc. |
| Model Info | GET /model-info | 200, 503 | model_id, version, metrics |
| Features | GET /features | 200, 503 | 18 canonical fields, 31 selected |

---

## 16. POST Endpoints

| Endpoint | Status | Validation | Notes |
|---|---|---|---|
| POST /predict | 200, 422, 503 | 18 fields, types, ranges | Raw + clipped + display |
| POST /explain | 200, 422, 503 | Same as predict | SHAP, additivity check |
| POST /what-if | 200, 422, 503 | Range + enum validation | Original immutable |

---

## 17. OpenAPI & Swagger

| Property | Value |
|---|---|
| Version | 3.1.0 |
| Title | HitRadar Pro API |
| Paths | 6 |
| Component schemas | 17 |
| Tags | system, model, prediction, explanation, what-if |
| SHA-256 | `cc5e7363...` |

Export: `5.UNG_DUNG/5.1.backend_api/openapi.json`

Swagger: `/docs` → 200, `/redoc` → 200

---

## 18. Postman

Collection: `5.UNG_DUNG/5.1.backend_api/hitradar_api_collection.json`
Requests: 7 (health, model-info, features, predict valid/invalid, explain, what-if)
Variable: `{{base_url}}` — no hardcoded URLs

Status: `COLLECTION_CREATED_NOT_EXECUTED` (JSON-valid, Swagger used for primary verification)

---

## 19. Environment & Port

- Port from `PORT` env var, default 8000
- Invalid port values rejected
- `.env.example` documents all variables
- No secrets in `.env.example`

---

## 20. API Smoke Tests

9 scenarios: health (2), model-info, features, predict (3), explain, what-if (2)
**9/9 PASS**

---

## 21. Full Pytest

| Metric | Value |
|---|---|
| Collected | 133 |
| Passed | **133** |
| Failed | 0 |
| Errors | 0 |
| Duration | ~10s |

---

## 22. Source Immutability

- Pipeline SHA-256: unchanged ✅
- No EPIC2 artifacts modified ✅
- No schema artifacts modified ✅
- No model artifacts written ✅

---

## 23. Warnings (3)

| ID | Nội dung | Impact |
|---|---|---|
| W1 | sklearn version mismatch (1.9.0 vs 1.8.0) | Non-blocking |
| W2 | httpx testclient deprecation | Non-blocking |
| W3 | Postman CLI not installed | Non-blocking |

---

## 24. Blockers

**0 blockers**

---

## 25. Final Decision

| Decision | Value |
|---|---|
| Feature 3.2 Status | **PASS_WITH_WARNINGS** |
| Feature 3.2 Decision | **ELIGIBLE_FOR_CLOSURE** |
| Feature 3.3 Gate | **MAY_BEGIN** |

---

## 26. Feature 3.3 Readiness

All 17 mandatory checks passed. Backend API functional, documented, and tested.

---

## 27. Evidence Index

| File | Path |
|---|---|
| Closure gate | `validation/feature_3_2_closure_gate.json` |
| Phase checkpoint | `checkpoints/feature_3_2_phase_6_checkpoint.json` |
| Pytest XML | `validation/pytest_feature_3_2.xml` |
| OpenAPI | `5.UNG_DUNG/5.1.backend_api/openapi.json` |
| Postman | `5.UNG_DUNG/5.1.backend_api/hitradar_api_collection.json` |
| .env.example | `epic3/feature_3_2/backend/.env.example` |
| This report | `Bao_cao_3/Báo cáo epic3/FEATURE_3_2_VALIDATION_REPORT.md` |
