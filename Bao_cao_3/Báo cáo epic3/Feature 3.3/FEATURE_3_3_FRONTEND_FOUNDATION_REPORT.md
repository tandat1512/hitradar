# Feature 3.3 — Frontend Foundation Report
## Streamlit Multi-Page App, API Client, Configuration

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 1 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Feature 3.2 Gate Check

| Check | Result |
|---|---|
| Feature 3.2 Status | PASS_WITH_WARNINGS |
| Feature 3.2 Decision | ELIGIBLE_FOR_CLOSURE |
| Feature 3.3 Gate | MAY_BEGIN ✅ |
| Blocker Count | 0 |

Backend endpoints confirmed from OpenAPI:
- GET /health
- GET /model-info
- GET /features
- POST /predict
- POST /explain
- POST /what-if

No API prefix — paths are direct.

Error response format (from Feature 3.0 contract):
- 400/404/500 → `{"detail": "message"}`
- 422 → `{"detail": [...]}`

---

## 2. Frontend Architecture

**Canonical path:** `epic3/feature_3_3/frontend/`

```
frontend/
├── app.py                    # Streamlit entry point
├── pages/
│   ├── 0_Home.py            # Project overview (Phase 1)
│   ├── 1_Predict.py         # Prediction form (Phase 2)
│   ├── 2_Explain.py          # SHAP explanation (Phase 3)
│   ├── 3_WhatIf.py          # What-If simulator (Phase 3)
│   ├── 4_Trends.py          # Music trends (Phase 4)
│   ├── 5_Model_Info.py      # Model metadata (Phase 2)
│   └── 6_Limitations.py     # Responsible use (Phase 1)
├── api/
│   ├── __init__.py
│   ├── client.py             # HitRadarAPIClient — HTTP only
│   ├── exceptions.py          # Typed exception hierarchy
│   └── models.py             # Lightweight response models
├── core/
│   ├── __init__.py
│   ├── config.py             # Settings from env
│   ├── navigation.py         # Page registry + sidebar
│   └── session.py            # Session state contract
├── components/               # Phase 2+
├── tests/                   # Phase 1 tests
└── validation/              # Evidence artifacts
```

---

## 3. API Client Design

**Class:** `HitRadarAPIClient`

### Methods

| Method | Endpoint | Response Type |
|---|---|---|
| `health()` | GET /health | `HealthResponse` |
| `get_model_info()` | GET /model-info | `ModelInfoResponse` |
| `get_features()` | GET /features | `FeaturesResponse` |
| `predict(payload)` | POST /predict | `PredictResponse` |
| `explain(payload)` | POST /explain | `ExplainResponse` |
| `what_if(base_features, changed_features)` | POST /what-if | `WhatIfResponse` |

### HTTP Library
`httpx` — timeout configured via `httpx.Timeout(connect=5.0, read=30.0, ...)`

### Timeout Policy

| Timeout | Default | Source |
|---|---|---|
| Connect | 5.0s | `BACKEND_CONNECT_TIMEOUT` |
| Read | 30.0s | `BACKEND_READ_TIMEOUT` |
| Write | 10.0s | hardcoded |
| Pool | 5.0s | hardcoded |

### URL Building
```python
url = f"{base_url.rstrip('/')}/{api_prefix.strip('/')}/{path.lstrip('/')}"
```
No double slashes, no path traversal.

### Request Headers
- `Accept: application/json`
- `Content-Type: application/json`
- `X-Request-ID: <uuid4>` (generated per request)

### Endpoint Registry
All paths read from OpenAPI contract — no guessed paths.

---

## 4. Exception Hierarchy

```
APIClientError (base)
├── APIConnectionError     → httpx.ConnectError
├── APITimeoutError       → httpx.TimeoutException
├── APIResponseError       → HTTP 400/404/500
│   ├── APIValidationError → HTTP 422
│   └── APIServiceUnavailableError → HTTP 503
└── APIContractError      → Malformed JSON or schema mismatch
```

---

## 5. Error Response Parsing

`parse_backend_error(status_code, response_body)` → typed exception.

Follows Feature 3.0 contract:
- 422: extracts field errors from `{"detail": [...]}`
- 503: `{"detail": "..."}`
- Other: `{"detail": "..."}`

No traceback exposed. Request ID preserved.

---

## 6. Configuration

All settings from `core/config.py` → `get_settings()`:

| Setting | Env Variable | Default |
|---|---|---|
| Backend URL | `BACKEND_BASE_URL` | `http://localhost:8000` |
| Connect timeout | `BACKEND_CONNECT_TIMEOUT` | `5.0` |
| Read timeout | `BACKEND_READ_TIMEOUT` | `30.0` |
| API prefix | `API_PREFIX` | `""` |
| Explain page | `ENABLE_EXPLAIN_PAGE` | `true` |
| What-if page | `ENABLE_WHAT_IF_PAGE` | `true` |

URL validation: `^https?://[^:/\s]+(:\d+)?$` — no path, no credentials embedded.

---

## 7. Session State Contract

Canonical keys defined in `core/session.py`:

| Key | Type | Purpose |
|---|---|---|
| `backend_status` | str | Connected/Degraded/Unavailable |
| `latest_request_id` | str | Last X-Request-ID |
| `current_prediction_input` | dict | PredictRequest |
| `current_prediction_result` | dict | Raw API response |
| `current_explanation` | dict | ExplainResponse |
| `current_whatif` | dict | WhatIfResponse |
| `whatif_base_prediction` | float | Cached for delta display |
| `cached_model_info` | dict | Model metadata cache |
| `cached_features` | dict | Features cache |
| `form_defaults_loaded` | bool | UI state |

No model objects, no API secrets stored.

---

## 8. Page Registry

| Page | ID | Phase | Backend Required |
|---|---|---|---|
| Home | home | 1 | No |
| Predict | predict | 2 | Yes |
| Explain | explain | 3 | Yes |
| What-If | whatif | 3 | Yes |
| Music Trends | trends | 4 | No |
| Model Info | model_info | 2 | Yes |
| Limitations | limitations | 1 | No |

Phase 1 skeleton pages: Home, Limitations only.
Backend-dependent pages stubbed as Phase 2+.

---

## 9. Navigation

Sidebar renders:
- App title + icon
- Backend status (Connected / Degraded / Unavailable)
- Page links

No model imports in navigation layer.
Deterministic, no session state pollution.

---

## 10. Hard Rules Compliance

| Rule | Status |
|---|---|
| No model loading in frontend | ✅ |
| No joblib/pickle | ✅ |
| No ModelService import | ✅ |
| No ExplainService import | ✅ |
| No WhatIfService import | ✅ |
| No direct SHAP computation | ✅ |
| No xgboost import | ✅ |
| No hardcoded prediction | ✅ |
| No fake API responses in production | ✅ |
| No absolute dev path in source | ✅ |
| No Git commit | ✅ |
| HTTP timeout configured | ✅ |
| Backend URL from config | ✅ |
| Error responses match Feature 3.0 | ✅ |

---

## 11. Test Suite (Phase 1)

Tests created (mock-based, no backend required):

| Test File | Coverage |
|---|---|
| `test_feature_3_3_project_structure.py` | Directory layout, __init__ files |
| `test_feature_3_3_api_client_methods.py` | health, model_info, features, predict, explain, what_if |
| `test_feature_3_3_api_client_errors.py` | timeout, 422, 503, 500, malformed JSON, headers |
| `test_feature_3_3_config_and_pages.py` | URL validation, settings, env vars |
| `test_feature_3_3_page_registry.py` | Page IDs, titles, session keys |
| `test_feature_3_3_no_model_access.py` | Forbidden imports scan + runtime check |

---

## 12. Validation Artifacts

| File | Purpose |
|---|---|
| `feature_3_2_to_feature_3_3_gate_validation.json` | Feature 3.2 gate check |
| `feature_3_3_canonical_path_validation.json` | Frontend path |
| `feature_3_3_frontend_environment.json` | Libraries |
| `feature_3_3_app_foundation_validation.json` | App init |
| `feature_3_3_page_registry.json` | 7 pages registered |
| `feature_3_3_navigation_validation.json` | Sidebar + nav |
| `feature_3_3_frontend_config_validation.json` | Config centralized |
| `feature_3_3_api_endpoint_registry.json` | Endpoints from OpenAPI |
| `feature_3_3_api_error_parsing_validation.json` | Error hierarchy |
| `feature_3_3_phase_1_session.json` | Session metadata |
| `feature_3_3_phase_1_gate.json` | Phase 1 gate |

---

## 13. Warnings & Blockers

**Warnings:** 0
**Blockers:** 0

---

## 14. Phase Gate

| Check | Status |
|---|---|
| Feature 3.2 gate valid | ✅ |
| Frontend path valid | ✅ |
| Streamlit foundation complete | ✅ |
| API client complete | ✅ |
| HTTP timeout policy valid | ✅ |
| Error parsing valid | ✅ |
| No direct model access | ✅ |
| No direct SHAP computation | ✅ |
| Tests present | ✅ |

**Status: PASS — MAY BEGIN Phase 2**
