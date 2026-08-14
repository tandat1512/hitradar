# Feature 3.7 — Phase 3 Report
## API Documentation & Limitations

**Feature:** 3.7 · **Phase:** 3/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09
**Status:** PASS_WITH_WARNINGS — MAY_BEGIN

---

## Phase 3 Evidence

```
API_DOCUMENTATION.md complete:             YES ✅
OpenAPI source valid:                      YES ✅ (6 routes, 13 schemas)
API path mismatches:                       0 ✅
Request-schema mismatches:                 0 ✅
Response-schema mismatches:                0 ✅
HTTP-status mismatches:                    0 ✅
Invalid request/response examples:          0 ✅
Limitation sources traceable:             YES ✅ (15 limitations)
Model/prediction limitations documented:   YES ✅
SHAP causal claims:                       0 ✅
What-if causal claims:                     0 ✅
Dashboard overgeneralization claims:       0 ✅
Offline fallback documented correctly:      YES ✅
Unsupported documentation claims:          0 ✅
Production code modified:                  NO ✅
Next phase:                               MAY_BEGIN
```

---

## 1. API Documentation

**Location:** `API_DOCUMENTATION.md` (repository root)

**Sources:** `openapi.json` (6 routes, 13 schemas), `prediction.py` Pydantic models, canonical E2E fixture.

### Endpoints Documented

| Method | Path | Request | Response | Status Codes |
|---|---|---|---|---|
| GET | `/health` | — | HealthResponse | 200 |
| GET | `/model-info` | — | ModelInfoResponse | 200, 503 |
| GET | `/features` | — | FeaturesResponse | 200, 503 |
| POST | `/predict` | PredictRequest (18 fields) | PredictResponse | 200, 422, 503 |
| POST | `/explain` | ExplainRequest (18 fields) | ExplainResponse | 200, 422, 503 |
| POST | `/what-if` | WhatIfRequest | WhatIfResponse | 200, 422, 503 |

**No API prefix** — routes are at root level.

### Example Requests

Canonical example from `artifacts/epic2/examples/example_input.json` (validated in Feature 3.5 E2E):
- Exact field values preserved
- Expected prediction_display: 46

### Request Contract Highlights

- `POST /predict` and `POST /explain`: all 18 fields required
- `POST /what-if`: `base_features` (18 fields) + `changed_features` (≥1 key, canonical field names only)
- Extra fields in PredictRequest: ignored with warning (`additionalProperties: allow`)
- Empty `changed_features`: raises 422

### Response Contract Highlights

- `prediction_raw`: may be outside [0, 100]
- `prediction_clipped`: clipped to [0, 100]
- `prediction_display`: rounded integer
- SHAP: 31 entries (one per selected feature); `top_features`: top 5 by absolute magnitude
- `request_id`: optional (nullable) in all responses

### Error Codes Documented

- **422**: Validation error — missing/out-of-range/invalid fields
- **503**: Model not loaded

---

## 2. Limitations Documentation

All 15 limitations traceable to actual evidence:

| Category | Count | Key Sources |
|---|---|---|
| DATA | 3 | `4_Trends.py`, `6_Limitations.py` |
| MODEL | 3 | `model_version.json`, `6_Limitations.py` |
| PREDICTION | 3 | `6_Limitations.py` |
| SHAP | 2 | `6_Limitations.py`, `openapi.json` |
| WHAT_IF | 2 | `6_Limitations.py` |
| DASHBOARD | 1 | `4_Trends.py` |
| OFFLINE_DEMO | 2 | offline contract |
| PERFORMANCE | 1 | API docs |
| FAIRNESS | 2 | `6_Limitations.py` |

---

## 3. Terminology Validation

All documentation correctly uses:
- **Regression score** (0–100), never "probability"
- **SHAP explains model behavior**, never "causes"
- **What-If compares model outputs**, never "proves real-world effect"
- **Available dataset shows**, never "all music"
- **Precomputed fallback**, never "backup model" for offline mode

---

## 4. Consistency with Feature 3.3

All limitation statements in API_DOCUMENTATION.md, USER_MANUAL.md, and HOW_TO_RUN_APP.md are semantically consistent with the Feature 3.3 `6_Limitations.py` page.

Semantic mismatches: **0**

---

## 5. Blockers & Warnings

**Blocker:** F37-B01 (no live Python env)
**Warnings:** F37-W05 (API examples from E2E fixture, not live-tested), F37-W06 (model metrics placeholder values), F37-W01 (TECHNICAL_APPENDIX.md Phase 4)

**Next phase: MAY_BEGIN**
