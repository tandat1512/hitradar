# Feature 3.3 — Responsible Use & UI Report
## Phase 6 — Limitations Page, UI Copy, Styling Consistency

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 6 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Limitations & Responsible Use Page

**File:** `pages/6_Limitations.py`

### Content Sections

| Section | Content |
|---|---|
| Project Context | Student research prototype disclaimer |
| Intended Use | Educational/research, ML behavior exploration |
| Non-Intended Use | Commercial decisions, causal claims, production use |
| What the Model Outputs | Popularity score (0–100), not probability or guarantee |
| Data Limitations | Dataset coverage, temporal bias, Spotify metric definition |
| Model Performance | MAE/RMSE/R² explanation, not "accuracy" |
| SHAP Explanations | Describes model behavior, not causation |
| What-If Simulator | Model prediction delta, not real-world effect |
| Bias & Fairness | Training data biases, non-musical factors |
| Human Judgment Required | Explicit requirement for human review |
| No Causal Interpretation | Warning: correlational ≠ causal |

### Sources Traced

- EPIC 2 ML Report (model performance, bias)
- Model Card (intended use, limitations)
- Feature 3.2 model-info (metric definitions)
- Product Contract (terminology)
- EPIC 3 requirements (responsible use checklist)

---

## 2. UI Claim Audit

**Scanned:** 12 files (pages + components)

### Prohibited Claims — All Cleared

| Claim Type | Result |
|---|---|
| "AI predicts hits accurately" | ✅ Not found |
| "Guaranteed hit" | ✅ Not found |
| "90% accuracy" | ✅ Not found |
| "SHAP proves why songs become popular" | ✅ Not found |
| "Increase danceability to increase real popularity" | ✅ Not found |
| "Production-grade" | ✅ Not found |
| "Industry-ready" | ✅ Not found |
| "Bias-free" | ✅ Not found |
| "Hit probability" | ✅ Not found |
| "Actual effect" (positive claim) | ✅ Not found |

All causal language found appears in correct disclaimer context:
- "SHAP explains how the model arrived at this prediction. **It describes model behavior, not causal relationships.**"
- "This shows how the **model's prediction** changes, not an actual effect."

---

## 3. Terminology Registry

Canonical terms enforced:

| Canonical Term | Used Correctly | Notes |
|---|---|---|
| Predicted Popularity | ✅ | Never "probability" |
| SHAP Explanation | ✅ | Never "feature accuracy" |
| What-If Simulation | ✅ | Never "actual effect" |
| Model Version | ✅ | Consistent across pages |
| Backend Unavailable | ✅ | Never HTTP internals |
| Request ID | ✅ | In captions, not exposed |

---

## 4. Error Copy

All error messages are user-friendly:

| Error | Message |
|---|---|
| Connection failed | "Cannot connect to backend" |
| Service unavailable | "Service temporarily unavailable" |
| Timeout | "Request timed out" |
| Validation failed | Field-level feedback |
| Contract error | "Unexpected response from backend" |

**Never exposed:** HTTPConnectionPool, stack trace, absolute paths, Python repr

---

## 5. Styling Validation

| Check | Status |
|---|---|
| Native Streamlit components only | ✅ |
| No custom CSS injection | ✅ |
| No `unsafe_allow_html=True` | ✅ |
| Charts: `use_container_width=True` | ✅ |
| No fixed large pixel widths | ✅ |
| `st.divider()` used for section breaks | ✅ |
| No `unsafe_allow_html` in any page | ✅ |
| No JavaScript injection | ✅ |

---

## 6. Phase Gate

| Check | Status |
|---|---|
| Responsible Use page complete | ✅ |
| Source traceability valid | ✅ |
| Unsupported accuracy claims: 0 | ✅ |
| Unsupported causal claims: 0 | ✅ |
| Terminology consistent | ✅ |
| Page titles consistent | ✅ |
| Error copy user-friendly | ✅ |
| Internal errors exposed: NO | ✅ |
| Styling complete | ✅ |
| No excessive unsafe HTML | ✅ |
| Business logic unchanged | ✅ |

**Status: PASS — MAY BEGIN Phase 7**
