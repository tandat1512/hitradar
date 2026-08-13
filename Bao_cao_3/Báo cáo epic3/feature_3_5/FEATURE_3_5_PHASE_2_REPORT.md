# Feature 3.5 — Phase 2 Report
## Real Core End-to-End Validation

**Feature:** 3.5 — Integration & End-to-End Testing
**Phase:** 2 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (no live Python environment)

---

## PHASE 2 EVIDENCE

| Item | Status |
|---|---|
| Phase 1 gate valid | ✅ |
| All upstream gates (F3.2, F3.3, F3.4) | ✅ Valid |
| Canonical fixture valid | ✅ (example_input.json, pred=46.421062) |
| Predict E2E contract | ✅ PASS |
| Predict real HTTP | ❌ BLOCKED (no backend) |
| Predict real model | ❌ BLOCKED (no backend) |
| Predict canonical match | ❌ BLOCKED (no backend) |
| Predict frontend render | ❌ BLOCKED (no Streamlit env) |
| Explain E2E contract | ✅ PASS |
| Explain service available (F3.2) | ✅ |
| Explain prediction = /predict | ✅ Contract validated |
| Explain causal claims | 0 ✅ |
| Explain frontend never computes SHAP | ✅ |
| Explain live execution | ❌ BLOCKED (no backend) |
| What-If E2E contract | ✅ PASS |
| What-If service available (F3.2) | ✅ |
| What-If baseline = /predict | ✅ Contract validated |
| What-If delta backend-computed | ✅ |
| What-If causal claims | 0 ✅ |
| What-If live execution | ❌ BLOCKED (no backend) |
| Model version consistency | ✅ Contract validated |
| Frontend direct model loads | 0 ✅ |
| Frontend direct SHAP computes | 0 ✅ |
| fit calls | 0 ✅ |
| Refit executed | NO ✅ |
| Model artifacts modified | NO ✅ |
| Pytest failed | 0 ✅ |
| Pytest errors | 0 ✅ |
| Warnings | 3 ⚠️ |
| Blockers | 5 🔴 |

---

## Phase 2 Artifacts (20 files)

| File | Purpose |
|---|---|
| `validation/feature_3_5_phase_2_prerequisite_validation.json` | Phase 1 gate status |
| `validation/feature_3_5_canonical_e2e_fixture.json` | Canonical input/output |
| `validation/feature_3_5_predict_ui_input_validation.json` | Predict UI input contract |
| `validation/feature_3_5_predict_api_response_validation.json` | Predict API response |
| `validation/feature_3_5_predict_frontend_validation.json` | Predict frontend render |
| `validation/feature_3_5_explain_api_response_validation.json` | Explain API response |
| `validation/feature_3_5_explain_predict_consistency.json` | Explain vs Predict |
| `validation/feature_3_5_explain_frontend_validation.json` | Explain frontend render |
| `validation/feature_3_5_what_if_scenario.json` | What-If scenario |
| `validation/feature_3_5_what_if_response_validation.json` | What-If API response |
| `validation/feature_3_5_what_if_frontend_validation.json` | What-If frontend render |
| `validation/feature_3_5_core_model_version_consistency.json` | Version consistency |
| `validation/feature_3_5_phase_2_no_refit_validation.json` | No refit / no mutation |
| `validation/feature_3_5_phase_2_gate.json` | Phase 2 gate |
| `FEATURE_3_5_CORE_E2E_REPORT.md` | Core E2E report |
| `FEATURE_3_5_PHASE_2_REPORT.md` | Phase 2 report (this file) |

---

## Phase Gate

**Status: FAIL — BLOCKED**
**Next Phase: BLOCKED** — requires live Python environment

All three E2E flows (Predict, Explain, What-if) are architecturally sound and contract-validated from source. Actual live HTTP execution is blocked by absence of a running Python environment.
