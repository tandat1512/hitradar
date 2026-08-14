# Feature 3.3 — Phase 6 Report
## Limitations & Responsible Use + UI Polish

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 6 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## PHASE 6 EVIDENCE

| Item | Status |
|---|---|
| Responsible Use page complete | YES |
| Unsupported accuracy claims | 0 |
| Unsupported causal claims | 0 |
| Causal language found only in disclaimer context | YES |
| UI terminology consistent | YES |
| Internal exception details exposed to user | NO |
| Button copy valid | YES |
| Error copy user-friendly | YES |
| `unsafe_allow_html=True` detected | NO |
| Minimum UI styling complete | YES |
| Charts use container width | YES |
| Business/API logic changed during styling | NO |
| **Next phase** | **MAY_BEGIN** |

---

## Key Findings

**Claim Audit:** 0 unsupported accuracy claims, 0 unsupported causal claims found across all 12 scanned files.

**Causal language** found only in:
- SHAP attribution caption: "It describes **model behavior**, not causal relationships."
- What-If caption: "This shows how the **model's prediction** changes, not an actual effect."
- Limitations page: "Correlational does not mean causal."

All in correct disclaimer context — not as positive product claims.

---

## Output Files

- **Limitations:** `pages/6_Limitations.py` (rewritten)
- **Tests:** `tests/test_feature_3_3_responsible_use.py`, `tests/test_feature_3_3_ui_claims_terminology.py`
- **Gate:** `validation/feature_3_3_phase_6_gate.json`
- **Reports:** `Bao_cao_3/Báo cáo epic3/FEATURE_3_3_RESPONSIBLE_USE_UI_REPORT.md`
