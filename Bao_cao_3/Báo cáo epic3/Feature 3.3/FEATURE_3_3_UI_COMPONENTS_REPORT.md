# Feature 3.3 — UI Components Report
## Phase 2 — Reusable Streamlit Component Library

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 2 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Component Library

```
components/
├── __init__.py
├── prediction_result.py   # render_prediction_result, render_prediction_warnings
├── shap_explanation.py   # render_shap_explanation, render_shap_empty_state
├── whatif_comparison.py  # render_whatif_comparison, render_whatif_empty_state
└── error_states.py      # render_error, render_warning, with_loading, empty states
```

---

## 2. Prediction Result Component

**Input:** `PredictResponse` (parsed by `api/models.py`)

**Renders:**
- Primary metric: `prediction_display` (0–100 scale)
- "Predicted Popularity" label — **never labeled as probability**
- Raw / clipped values shown only if they differ
- Status badge (SUCCESS / etc.)
- Model ID, version
- Request ID (for debug)
- Backend warnings

**Terminology:** "Predicted Popularity" — not "hit probability" or "success likelihood"

**Validation:**
- Uses `prediction_display` as primary (not raw)
- Does not clamp scores — respects API contract
- No model recomputation

---

## 3. SHAP Explanation Component

**Input:** `ExplainResponse`

**Renders:**
- Attribution caption (on every render): *"SHAP explains how the model arrived at this prediction. It describes model behavior, not causal relationships."*
- Prediction score
- Base value
- Contributions table: feature, value, direction icon (🔺 positive / 🔻 negative / ➖ neutral), contribution value
- Sorted by contribution magnitude
- Request ID

**Direction correctness:**
- Positive contribution → type="positive" → 🔺
- Negative contribution → type="negative" → 🔻

**Terminology:** "model behavior" — never "causes" or "effect"

**No SHAP computation in frontend** — all values come from `ExplainResponse`

---

## 4. What-If Comparison Component

**Input:** `WhatIfResponse`

**Renders:**
- Attribution caption: *"This shows how the model's prediction changes, not an actual effect."*
- Prediction before (baseline)
- Prediction after (modified)
- Delta (🔺/▼/➖)
- Direction summary text
- Changed fields list
- Request ID

**Delta source:** `WhatIfResponse.delta` from backend — **not recomputed in frontend**

**Terminology:** "model's prediction changes" — never "actual effect"

---

## 5. Error Component

**Input:** `Exception` (typed API exceptions)

**Renders per type:**

| Exception | Title | Content |
|---|---|---|
| `APIValidationError` | Request validation failed | Field errors with readable messages |
| `APIServiceUnavailableError` | Service temporarily unavailable | Retry guidance |
| `APITimeoutError` | Request timed out | Timeout guidance |
| `APIConnectionError` | Cannot connect to backend | Backend startup guidance |
| `APIResponseError` | Backend error (code) | HTTP code |
| `APIContractError` | Unexpected response format | Contract review notice |
| Generic | Something went wrong | Generic fallback |

**Never exposed:** stack trace, absolute file paths, Python repr, secrets

**Request ID** shown in caption for all error types

---

## 6. Warning & Empty States

| State | Trigger | Message |
|---|---|---|
| Backend degraded | `health()` returns degraded | "Backend is in degraded mode..." |
| Provisional result | any model result | "Result based on current model version..." |
| Predict empty | before user submits | "Enter song features and click Predict..." |
| SHAP empty | before explanation | "Enter song features and click Explain..." |
| What-if empty | before comparison | "Create a baseline prediction first..." |
| Backend unavailable | connection failed | Backend startup instructions |

---

## 7. Loading Pattern

```python
from components.error_states import with_loading

result = with_loading("Predicting...", client.predict, payload)
```

Uses `st.spinner()` — no external loading libraries.

---

## 8. Component Hard Rules

| Rule | Status |
|---|---|
| No network calls in components | ✅ |
| No model loading | ✅ |
| No SHAP computation | ✅ |
| No causal claims | ✅ |
| No probability terminology | ✅ |
| No hardcoded predictions | ✅ |
| Terminology from contract | ✅ |
| Request ID preserved | ✅ |
| Error safe from traceback | ✅ |

---

## 9. Fixture Contract

Test fixtures mirror OpenAPI schemas exactly — no extra fields, no invented data.

| Fixture | Type | Source |
|---|---|---|
| `predict_success_fixture` | PredictResponse | OpenAPI schema |
| `explain_success_fixture` | ExplainResponse | OpenAPI schema |
| `whatif_success_fixture` | WhatIfResponse | OpenAPI schema |
| `health_healthy_fixture` | HealthResponse | OpenAPI schema |
| `validation_error_fixture` | Feature 3.0 contract | `{"detail": [...]}` |

---

## 10. Test Coverage

| Test File | Coverage |
|---|---|
| `test_feature_3_3_prediction_component.py` | display value, warnings, metadata, no probability |
| `test_feature_3_3_shap_component.py` | direction, validity, empty, no causal |
| `test_feature_3_3_whatif_and_error.py` | delta source, direction, error types, no network, loading |

---

## 11. Warnings & Blockers

**Warnings:** 0
**Blockers:** 0

---

## 12. Phase Gate

| Check | Status |
|---|---|
| Prediction component complete | ✅ |
| Prediction not probability | ✅ |
| SHAP component complete | ✅ |
| No causal claims in SHAP | ✅ |
| No SHAP computation in frontend | ✅ |
| What-if component complete | ✅ |
| Delta from backend | ✅ |
| No causal claims in What-if | ✅ |
| Error component (7 types) | ✅ |
| Warning states | ✅ |
| Loading pattern | ✅ |
| Empty states | ✅ |
| Components: no network | ✅ |
| Components: no model loading | ✅ |
| Fixture contract valid | ✅ |

**Status: PASS — MAY BEGIN Phase 3**
