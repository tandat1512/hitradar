# Feature 3.7 — Phase 3 Report
## API Contract Documentation & Limitations

**Feature:** 3.7 · **Phase:** 3/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09
**Status:** PASS_WITH_WARNINGS — MAY_BEGIN

---

## Phase 3 Evidence

```
API_DOCUMENTATION.md created:                   YES ✅
OpenAPI source valid:                           YES ✅
OpenAPI routes documented:                       6 ✅
API path mismatches:                            0 ✅
Request-schema mismatches:                      0 ✅
Response-schema mismatches:                     0 ✅
HTTP-status mismatches:                        0 ✅
Invalid examples:                               0 ✅
Limitation source registry complete:            YES ✅
Limitations documented:                         15 ✅
SHAP causal claims:                            0 ✅
What-if causal claims:                         0 ✅
Dashboard overgeneralizations:                  0 ✅
Offline fallback correctly described:             YES ✅
Prediction terminology valid:                   YES ✅
Responsible-use consistency:                    0 mismatches ✅
Unsupported documentation claims:               0 ✅
Production code modified:                       NO ✅
Next phase:                                   MAY_BEGIN
```

---

## 1. Feature 3.7 Gate

Feature 3.7 Phase 1: FAIL (intentional — F37-B01 no Python env; F37-B02 resolved)
Feature 3.7 Phase 2: PASS_WITH_WARNINGS (F37-W04 walkthrough not live-executed)
Feature 3.7 Phase 3: **PASS_WITH_WARNINGS** (F37-W05 API examples, F37-W06 metrics placeholder)

## 2. OpenAPI Source

`5.UNG_DUNG/5.1.backend_api/openapi.json` — validated as canonical source:
- 6 routes: GET /health, /model-info, /features; POST /predict, /explain, /what-if
- 13 schemas; OpenAPI 3.1.0
- No API prefix (routes at root level)
- `request_id` nullable in all responses

## 3. API_DOCUMENTATION.md

All endpoints documented with request/response schemas, status codes, and example workflows.
Canonical example: from Feature 3.5 E2E fixture (validated in Feature 3.1 artifact validation).

## 4. Limitations

15 limitations across 8 categories, all with evidence-based sources:
- DATA: 3 (temporal coverage, sampling, popularity definition, geographic bias)
- MODEL: 3 (XGBoost regression, regression ≠ classification, metrics)
- PREDICTION: 3 (not causal, not commercial guarantee, academic prototype)
- SHAP: 2 (not causal, model behavior only)
- WHAT_IF: 2 (model comparison only, no real-world effect)
- DASHBOARD: 1 (available dataset scope)
- OFFLINE_DEMO: 2 (precomputed, limited scenarios)
- PERFORMANCE: 1 (no SLA)

## 5. Blockers & Warnings

**Blockers:** F37-B01 (no live Python env).
**Warnings:** F37-W05 (API examples from E2E fixture, not live), F37-W06 (model metrics placeholder values), F37-W01 (TECHNICAL_APPENDIX.md Phase 4).

## 6. Artifacts Created

Phase 3 validation artifacts in `feature_3_7/validation/`:
`openapi_source_validation.json`, `api_endpoint_inventory.json`, `api_path_validation.json`, `api_request_contract.json`, `api_response_contract.json`, `api_documentation_consistency.csv`, `limitation_source_registry.json`, `responsible_use_consistency.json`, `phase_3_claim_audit.json`, `limitation_coverage_matrix.csv`, `phase_3_gate.json`.

## 7. Next Steps for Phase 4

1. Create `TECHNICAL_APPENDIX.md` (final README link — Phase 4)
2. Resolve final README broken link
3. End-to-end documentation review
