# FEATURE 3.1 — Phase 3 Report
**Phase:** 3/5 — Inference Asset Validation
**Feature:** 3.1 — Artifact Intake & Validation Gate
**Person in Charge:** Minh
**Session:** 2026-08-04

---

## Prerequisite

Phase 2 gate: `PASS_WITH_WARNINGS`, `next_phase = MAY_BEGIN`. Validated.

---

## Model Metrics

Source: `7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json`

| Metric | Value | Stage |
|--------|-------|-------|
| MAE | 17.647 | test |
| RMSE | 21.013 | test |
| R² | 0.070 | test |
| Underprediction Rate | 67.8% | test |

All finite, from test split (85,876 rows). Model ID `EXP24-XGB-FINAL-001`, version `1.0.0`.

---

## Residual Statistics

Source: `7.ML/7.8.model_evaluation/residuals/residual_statistics.json`

Convention: `actual - predicted` (inferred from consistency).
Mean residual = +4.857. Model systematically underpredicts popularity.
Warning: convention not explicitly documented in artifact.

---

## Metric Consistency

MAE, RMSE, R², residual stats, and SHAP manifests all reference the same model (`EXP24-XGB-FINAL-001`, `1.0.0`, test split). No inconsistencies found.

---

## SHAP Assets

16 SHAP assets found and validated:
- Background (raw + transformed): ✅
- SHAP values (5,000 × 49): ✅
- Base values: ✅
- Feature mapping (49 features): ✅
- Additivity validation (pass rate 100%): ✅
- Global importance CSVs: ✅
- Additivity max error: 6.75e-05 (< 0.001 tolerance)

**SHAP recomputed:** NO
**EPIC 3 requirement:** SHAP is required for `/explain` endpoint.

---

## Example Input

18 fields, all valid per input schema. No target, no unknown fields.

---

## Prediction

| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| prediction_raw | 46.421062 | 46.421062 | ✅ Exact |
| model_version | 1.0.0 | 1.0.0 | ✅ Match |

---

## Output Schema

Valid: required fields, types, finite values, model version.

---

## Determinism

3 runs → all `46.421062`. Max diff: 0.0. **Deterministic: YES.**

---

## No-Refit

fit = 0, fit_transform = 0, partial_fit = 0. Model hash unchanged.

---

## Phase Gate: PASS WITH_WARNINGS

| Criterion | Status |
|-----------|--------|
| Model metrics valid | ✅ |
| Residual stats valid | ✅ |
| Metric consistency valid | ✅ |
| SHAP assets valid | ✅ |
| Example input valid | ✅ |
| Prediction executed | ✅ |
| Output schema valid | ✅ |
| Prediction matches expected | ✅ |
| Prediction deterministic | ✅ |
| Fit calls = 0 | ✅ |
| SHAP recomputed | NO |
| Source artifacts modified | NO |

**Warnings:** Residual convention not explicitly documented; sklearn version mismatch (1.9.0 vs 1.8.0).
**Blockers:** None.
**Next Phase: MAY_BEGIN**
