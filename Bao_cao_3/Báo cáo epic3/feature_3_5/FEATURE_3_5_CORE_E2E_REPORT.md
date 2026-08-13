# Feature 3.5 — Core E2E Report
## Phase 2 — Real Predict, Explain, What-if Validation

**Feature:** 3.5 — Integration & End-to-End Testing
**Phase:** 2 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (no live Python environment)

---

## 1. Prerequisite

Phase 1 Gate: FAIL — BLOCKED. All contract/architecture validations passed; live execution blocked by no Python environment.

---

## 2. Canonical Fixture

| Field | Value |
|---|---|
| Input path | `7.ML/7.10.model_packaging/package/examples/example_input.json` |
| Output path | `7.ML/7.10.model_packaging/package/examples/example_output.json` |
| Input fields | 18 (duration_min, explicit, release_year, …, time_signature) |
| Expected prediction | **46.421062** |
| Tolerance | ±0.001 (from Feature 3.1) |
| Model ID | `EXP24-XGB-FINAL-001` |
| Model version | `1.0.0` |

**Not modified.** This is the one-and-only canonical input for all Phase 2 E2E tests.

---

## 3. Architecture Validation

All three E2E flows verified from source code:

```
Streamlit (1_Predict.py / 2_Explain.py / 3_WhatIf.py)
  → HitRadarAPIClient (httpx)
    → HTTP POST /predict  |  /explain  |  /what-if
      → FastAPI (api.py)
        → ModelService / ExplainService / WhatIfService
          → PipelineLoader → model artifacts
            → HTTP response
              → PredictResponse / ExplainResponse / WhatIfResponse
                → render_prediction_result / shap_explanation / whatif_comparison
```

| Check | Predict | Explain | What-If |
|---|---|---|---|
| HTTP transport | ✅ httpx | ✅ httpx | ✅ httpx |
| Backend service | ✅ ModelService | ✅ ExplainService | ✅ WhatIfService |
| Real model artifact | ✅ PipelineLoader | ✅ SHAP artifacts | ✅ PipelineLoader |
| Direct frontend model load | 0 ✅ | 0 ✅ | 0 ✅ |
| Direct frontend SHAP compute | 0 ✅ | 0 ✅ | 0 ✅ |

---

## 4. Predict E2E

### Contract
| Field | Value |
|---|---|
| Endpoint | `POST /predict` |
| Request | 18-field PredictRequest |
| Response | PredictResponse (status, prediction_raw, prediction_clipped, prediction_display, model_id, model_version, package_version, timestamp, warnings) |
| Canonical expected | 46.421062 |
| Tolerance | ±0.001 |

### Validation stages
| Stage | Status |
|---|---|
| UI input (18 fields, no target exposed) | ✅ Contract validated |
| HTTP request (POST, JSON, X-Request-ID) | ✅ Contract validated |
| Backend ModelService invoked | ✅ Contract validated |
| Response schema (all fields) | ✅ Contract validated |
| Actual HTTP request (live) | ❌ BLOCKED — no Python env |
| Prediction matches canonical 46.421062 | ❌ BLOCKED — no backend |

---

## 5. Explain E2E

### Contract
| Field | Value |
|---|---|
| Endpoint | `POST /explain` |
| Request | Same 18-field PredictRequest |
| Response | ExplainResponse (status, prediction_raw, base_value, shap_values dict, top_features list) |
| Additivity | sum(shap_values) + base_value ≈ prediction_raw (tol 0.01) |
| Frontend SHAP compute | **NOT DONE by frontend** — backend computes |

### Validation stages
| Stage | Status |
|---|---|
| ExplainService confirmed in Feature 3.2 | ✅ |
| SHAP artifacts from EPIC 2 | ✅ |
| Prediction consistent with /predict | ✅ Contract validated (tol 0.001) |
| Frontend never computes SHAP | ✅ Confirmed from source |
| No causal wording in shap_explanation.py | ✅ |
| Actual HTTP /explain (live) | ❌ BLOCKED — no Python env |

---

## 6. What-If E2E

### Contract
| Field | Value |
|---|---|
| Endpoint | `POST /what-if` |
| Request | {base_features: 18 fields, changed_features: dict} |
| Response | WhatIfResponse (prediction_before, prediction_after, delta, changed_fields) |
| Delta | backend_delta = prediction_after - prediction_before |
| Baseline consistency | prediction_before must match /predict result (tol 0.001) |

### Modification selection
Uses canonical input. One audio feature modified within valid range:
- `energy: 0.793 → 0.95` (within [0, 1])
- `danceability: 0.785 → 0.95` (alternative)
- `valence: 0.655 → 0.9` (alternative)
- `loudness: -7.915 → -3.0` (alternative)

Selected at live test time from actual `/features` response.

### Validation stages
| Stage | Status |
|---|---|
| WhatIfService confirmed in Feature 3.2 | ✅ |
| Baseline matches /predict for same input | ✅ Contract validated (tol 0.001) |
| Delta computed by backend (not frontend) | ✅ |
| Frontend never computes delta directly | ✅ Confirmed from source |
| No causal what-if wording | ✅ |
| Actual HTTP /what-if (live) | ❌ BLOCKED — no Python env |

---

## 7. Model Version Consistency

| Endpoint | model_id | model_version |
|---|---|---|
| GET /model-info | EXP24-XGB-FINAL-001 | 1.0.0 |
| POST /predict | EXP24-XGB-FINAL-001 | 1.0.0 |
| POST /explain | EXP24-XGB-FINAL-001 | 1.0.0 |
| POST /what-if | EXP24-XGB-FINAL-001 | 1.0.0 |

**Contract validated.** Live verification BLOCKED.

---

## 8. No-Refit / No-Mutation

| Check | Status |
|---|---|
| fit() called during Phase 2 | 0 ✅ (backend only — no live test) |
| fit_transform() called | 0 ✅ |
| partial_fit() called | 0 ✅ |
| Model artifact modified | NO ✅ |
| Source dataset modified | NO ✅ |

**Confirmed from design.** Backend PipelineLoader loads artifacts at startup, E2E only consumes predictions.

---

## 9. Causal Claim Audit

All three pages scanned for causal language:

| Page | Causal claims found |
|---|---|
| 1_Predict.py | 0 ✅ |
| 2_Explain.py | 0 ✅ |
| 3_WhatIf.py | 0 ✅ |
| shap_explanation.py | 0 ✅ |
| whatif_comparison.py | 0 ✅ |

**"causes", "led to", "makes songs", "will increase" — all banned.**

---

## 10. Summary

| Workflow | Contract Valid | Live Execution | Blocked By |
|---|---|---|---|
| Predict E2E | ✅ | ❌ | No Python env |
| Explain E2E | ✅ | ❌ | No Python env |
| What-If E2E | ✅ | ❌ | No Python env |
| Model version consistency | ✅ | ❌ | No Python env |
| No-refit confirmed | ✅ | ⚠️ | Backend startup required |
| Causal claims | 0 ✅ | ✅ | — |

**All three E2E flows are architecturally sound and contract-validated. Live execution is blocked.**

---

## 11. Path Forward

To unblock Phase 2 live execution:

1. Start backend: `cd 5.UNG_DUNG/5.1.backend_api && python -m uvicorn api:app --host 127.0.0.1 --port 8000`
2. Verify `GET /health` → `{"status": "healthy", "model_loaded": true}`
3. Run canonical Predict: `POST /predict` with example_input.json
4. Verify prediction = 46.421062 ± 0.001
5. Run Explain and What-If with same canonical input
6. Verify model version consistency across all responses
7. Re-run Phase 2 with live evidence
