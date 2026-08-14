# Feature 3.3 — Phase 4 Report
## SHAP Explanation + What-If Simulator

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 4 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## PHASE 4 EVIDENCE

| Item | Status |
|---|---|
| SHAP Explanation page complete | YES |
| POST /explain integration valid | YES |
| Frontend computes SHAP directly | NO ✅ |
| Frontend reads SHAP artifacts directly | NO ✅ |
| Causal wording detected | NO ✅ |
| What-If page complete | YES |
| POST /what-if integration valid | YES |
| Target can be modified | NO ✅ |
| What-if presented as causal effect | NO ✅ |
| Cross-page prediction state valid | YES |
| No direct model access | YES |
| No training | NO ✅ |
| No refit | NO ✅ |
| **Next phase** | **MAY_BEGIN** |

---

## Output Files

- **SHAP page:** `pages/2_Explain.py`
- **What-If page:** `pages/3_WhatIf.py`
- **Tests:** `test_feature_3_3_shap_page.py`, `test_feature_3_3_whatif_page.py`, `test_feature_3_3_cross_page.py`
- **Gate:** `validation/feature_3_3_phase_4_gate.json`
- **Report:** `Bao_cao_3/Báo cáo epic3/FEATURE_3_3_SHAP_WHAT_IF_REPORT.md`
