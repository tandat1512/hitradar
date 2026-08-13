# Feature 3.5 — Negative E2E Report
## Phase 3 — Error Handling, Invalid Input & Recovery

**Feature:** 3.5 — Integration & End-to-End Testing
**Phase:** 3 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (no live Python environment)

---

## 1. Test Contract Source

All test contracts derive from **actual verified evidence**:

| Source | Content |
|---|---|
| `5.UNG_DUNG/5.1.backend_api/models/prediction.py` | Pydantic constraints for all 18 fields |
| `5.UNG_DUNG/5.1.backend_api/openapi.json` | Endpoint contracts, status codes |
| `epic3/feature_3_3/frontend/api/exceptions.py` | Exception hierarchy, error parsing |
| `epic3/feature_3_3/frontend/components/error_states.py` | User-facing error rendering |

No test contract is invented. Every value, status code, and message is traced to actual code.

---

## 2. Pydantic Constraints (18 fields)

All 18 fields are non-nullable required. Key bounds:

| Field | Type | Min | Max | Constraint |
|---|---|---|---|---|
| duration_min | float | 0.0 | 120.0 | ge, le |
| explicit | bool | — | — | required |
| release_year | int | 1900 | 2100 | ge, le |
| release_month | float | 1.0 | 12.0 | ge, le |
| decade | int | 1900 | 2100 | ge, le |
| release_precision | str | — | — | pattern: day/month/year |
| danceability | float | 0.0 | 1.0 | ge, le |
| energy | float | 0.0 | 1.0 | ge, le |
| key | int | 0 | 11 | ge, le |
| loudness | float | -60.0 | 0.0 | ge, le |
| mode | int | 0 | 1 | ge, le |
| speechiness–valence | float | 0.0 | 1.0 | ge, le |
| tempo | float | 0.0 | 300.0 | ge, le |
| time_signature | float | — | — | required |

**Pydantic extra policy: `allow`** — extra fields are accepted but ignored.

---

## 3. Error Response Contract

| Error type | HTTP status | Frontend message | Source |
|---|---|---|---|
| Connection refused | — (exception) | Cannot connect to backend | `_render_connection_error` |
| Timeout | — (exception) | Request timed out | `_render_timeout_error` |
| Validation error (422) | 422 | Request validation failed | `_render_validation_error` |
| Service unavailable (503) | 503 | Service temporarily unavailable | `_render_service_unavailable` |
| Contract error | — (exception) | Unexpected response from backend | `_render_contract_error` |

**Guarantees:**
- No Python traceback exposed
- No internal file paths exposed
- Request ID shown in all error cases
- No hardcoded hints that reveal internal architecture

---

## 4. 18-Negative Scenario Summary

| ID | Scenario | Expected HTTP | Expected Type | Live? |
|---|---|---|---|---|
| E2E-001 | Backend unavailable | CLIENT_ERROR | APIConnectionError | ❌ |
| E2E-002 | Timeout (>30s) | CLIENT_ERROR | APITimeoutError | ❌ |
| E2E-003 | Missing 1 field | 422 | APIValidationError | ❌ |
| E2E-004 | Missing 2 fields | 422 | APIValidationError | ❌ |
| E2E-005 | Range LOW (danceability=-0.001) | 422 | APIValidationError | ❌ |
| E2E-006 | Range HIGH (danceability=1.001) | 422 | APIValidationError | ❌ |
| E2E-007 | Extra unknown field | 200 | PredictResponse | ❌ |
| E2E-008 | Target injection | 200 | PredictResponse | ❌ |
| E2E-009 | Wrong type string in numeric | 422 | APIValidationError | ❌ |
| E2E-010 | Wrong structure array in scalar | 422 | APIValidationError | ❌ |
| E2E-011 | Null in non-nullable field | 422 | APIValidationError | ❌ |
| E2E-012 | Empty payload {} | 422 | APIValidationError | ❌ |
| E2E-013 | Malformed JSON | 4xx | HTTPException | ❌ |
| E2E-014 | Invalid categorical (release_precision=invalid) | 422 | APIValidationError | ❌ |
| E2E-015 | Range LOW (key=-1) | 422 | APIValidationError | ❌ |
| E2E-016 | Range HIGH (key=12) | 422 | APIValidationError | ❌ |
| E2E-017 | Backend recovers after down | 200 | PredictResponse | ❌ |
| E2E-018 | Valid request after validation error | 200 | PredictResponse | ❌ |

**All 18 scenarios contract-validated. Live execution blocked.**

---

## 5. Key Design Decisions

### Extra Field Policy: `allow`
Pydantic accepts extra fields silently. They are NOT passed to the model feature matrix. The model is protected by PipelineLoader which constructs the feature matrix from known audio features only.

### Target Injection: Allowed but Ignored
`target_popularity` is accepted by Pydantic but PipelineLoader constructs the feature matrix from only the 18 canonical fields. Target cannot affect predictions.

### Silent Clipping: NOT Done
Frontend sends user values as entered. Backend enforces constraints. No silent modification.

### Timeout: 30 seconds
Configured via `httpx.Timeout(read=30.0)` in HitRadarAPIClient.

---

## 6. 500 Errors

**Expected: 0** — All invalid-input scenarios should return 422 or CLIENT_ERROR, never 500.

Any 500 from input validation = **BLOCKER**.

Current contract: validation errors → 422 ✅.

---

## 7. Traceback & Internal Path Exposure

Checked in `error_states.py`:

| Function | Traceback | Internal Path |
|---|---|---|
| `_render_connection_error` | ❌ Never | ❌ Never |
| `_render_timeout_error` | ❌ Never | ❌ Never |
| `_render_validation_error` | ❌ Never | ❌ Never |
| `_render_service_unavailable` | ❌ Never | ❌ Never |
| `_render_http_error` | ❌ Never | ❌ Never |
| `_render_contract_error` | ❌ Never | ❌ Never |
| `_render_generic_error` | ❌ Never | ❌ Never |

---

## 8. Path Forward

To execute live negative tests:
1. Start backend: `cd 5.UNG_DUNG/5.1.backend_api && python -m uvicorn api:app --host 127.0.0.1 --port 8000`
2. For each scenario in error matrix (18 tests), fire actual HTTP request
3. Capture actual status codes and response bodies
4. Verify no 500 errors
5. Start frontend and verify error UX
