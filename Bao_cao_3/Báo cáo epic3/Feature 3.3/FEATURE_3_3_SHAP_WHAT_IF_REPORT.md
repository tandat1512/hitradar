# Feature 3.3 — SHAP & What-If Pages Report
## Phase 4 — SHAP Explanation + What-If Simulator

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 4 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. SHAP Explanation Page

**File:** `pages/2_Explain.py`

### Flow

```
Page load
  → Check current_prediction_input in session state
  → If missing → empty state + stop
  → Show input summary (6 key fields + expander for all 18)
  → POST /explain with cached input (st.spinner)
  → Success → render_shap_explanation() + save to session
  → Attribution reminder caption
  → CTA to What-If page
```

### Version Warning

If `cached_model_info.model_version` ≠ `current_prediction_result.model_version`:
→ ⚠️ "The cached prediction was made with a different model version."

### Attribution

Every render includes:
> "SHAP values show how the model produced this prediction. They describe **model behavior**, not causal relationships."

### Hard Rules

| Rule | Status |
|---|---|
| No shap import | ✅ |
| No SHAP artifact read (.npy/.joblib) | ✅ |
| No direct model access | ✅ |
| No causal wording ("causes", "will increase") | ✅ |
| Has "model behavior" attribution | ✅ |
| Uses POST /explain API | ✅ |

---

## 2. What-If Simulator Page

**File:** `pages/3_WhatIf.py`

### Flow

```
Page load
  → Load baseline from current_prediction_input + current_prediction_result
  → If missing → empty state + stop
  → Show baseline score + input summary
  → User selects fields to modify (multiselect)
  → st.form renders sliders/selectboxes for selected fields
  → Submit → POST /what-if with {base_features, changed_features}
  → render_whatif_comparison()
  → Reset button to clear modifications
```

### Modifiable Fields

Excluded from modification:
- `target` ❌
- `model_version_override` ❌
- `selected_features` ❌
- `request_id` ❌

### Payload

```python
client.what_if(
    base_features=baseline_input,    # 18 fields from session
    changed_features={fname: new_val, ...}
)
```

### Attribution

> "This shows how the model's prediction changes, not an actual effect."

### Hard Rules

| Rule | Status |
|---|---|
| No model import | ✅ |
| No causal wording | ✅ |
| Target not modifiable | ✅ |
| Delta from backend | ✅ |
| Baseline not overwritten | ✅ |
| Uses POST /what-if API | ✅ |

---

## 3. Cross-Page State

| Session Key | Set By | Read By |
|---|---|---|
| `current_prediction_input` | Predict page | SHAP, What-If |
| `current_prediction_result` | Predict page | SHAP, What-If |
| `current_explanation` | SHAP page | — |
| `current_whatif` | What-If page | — |
| `cached_model_info` | Predict page | Home, SHAP |
| `cached_features` | Predict page | What-If |

`current_prediction_result` is **never overwritten** by What-If results.
What-If saves to `current_whatif` only.

---

## 4. Hard Rules Summary

| Rule | SHAP | What-If |
|---|---|---|
| No direct SHAP computation | ✅ | — |
| No SHAP artifact read | ✅ | — |
| No model loading | ✅ | ✅ |
| No causal wording | ✅ | ✅ |
| API-only (POST /explain, /what-if) | ✅ | ✅ |
| Target modifiable | — | ❌ |
| Delta from backend | — | ✅ |
| Baseline preserved | ✅ | ✅ |

---

## 5. Tests

| File | Coverage |
|---|---|
| `test_feature_3_3_shap_page.py` | no shap import, no causal claim, session reuse, empty state |
| `test_feature_3_3_whatif_page.py` | no model import, payload schema, no causal, target excluded |
| `test_feature_3_3_cross_page.py` | session keys, no baseline overwrite, state contracts |

---

## 6. Phase Gate

| Check | Status |
|---|---|
| SHAP page complete | ✅ |
| POST /explain integration | ✅ |
| No direct SHAP computation | ✅ |
| No SHAP artifact access | ✅ |
| No causal wording | ✅ |
| What-If page complete | ✅ |
| POST /what-if integration | ✅ |
| Target modifiable | ❌ |
| No causal wording | ✅ |
| Cross-page state valid | ✅ |
| No direct model access | ✅ |

**Status: PASS — MAY BEGIN Phase 5**
