# Feature 3.7 — Technical Appendix Report

**Feature:** 3.7 · **Phase:** 4/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09
**Status:** PASS — MAY_BEGIN

---

## Phase 4 Evidence

```
TECHNICAL_APPENDIX.md complete:               YES ✅
System architecture matches implementation:   YES ✅
Model fact mismatches:                       0 ✅
Feature-count mismatches:                    0 ✅
Metric mismatches:                          0 ✅
SHAP implementation claims unsupported:      0 ✅
Performance-number mismatches:                0 ✅
E2E-claim mismatches:                       0 ✅
Broken links:                               0 ✅
Personal machine paths in technical docs:    0 ✅
Unsupported technical claims:                0 ✅
New training experiments executed:           NO ✅
Model artifacts modified:                    NO ✅
Next phase:                                 MAY_BEGIN
```

---

## 1. Technical Appendix Overview

**Location:** `TECHNICAL_APPENDIX.md` (repository root)
**Sections:** 30 (§1–§30)

All technical claims traceable to actual evidence files. No new experiments run. No training executed.

---

## 2. Architecture Validation

| Path | Verified |
|---|---|
| User → Streamlit → HTTP → FastAPI → model | ✅ |
| Dashboard (Music Trends) reads local CSV | ✅ (no backend required) |
| SHAP computed by backend only | ✅ (frontend displays only) |
| Offline mode = precomputed fallback | ✅ |
| run_all.py polls health (no fixed sleep) | ✅ |

---

## 3. Model Facts

| Fact | Value | Source |
|---|---|---|
| Model ID | `EXP24-XGB-FINAL-001` | `model_version.json` |
| Version | `1.0.0` | `model_version.json` |
| Family | XGBoost | `model_version.json` |
| Feature set | FS23-SELECTED | `model_version.json` |
| Pipeline SHA-256 | `7ff4b11...` | `artifact_manifest.json` |
| Pipeline class | `HitRadarInferencePipeline` | Feature 3.1 model load validation |

---

## 4. Feature Layers (Distinguished)

| Layer | Count | Terminology in Appendix |
|---|---|---|
| Raw input (user-supplied) | 18 | "18 canonical input fields (raw)" |
| Selected features (after feature selection) | 31 | "31 selected features (18 raw + 13 engineered)" |
| Transformed model matrix | 49 | "49 model matrix columns after pipeline transformation" |

---

## 5. Model Metrics

From `feature_3_1_model_metrics_validation.json` (test set, 85,876 rows):

| Metric | Value |
|---|---|
| MAE | 17.65 |
| RMSE | 21.01 |
| R² | 0.070 |
| Mean Residual | +4.86 (underprediction) |
| Underprediction Rate | 67.8% |

R² described as "low" with context (explains ~7% of variance) — not framed as accuracy.

---

## 6. SHAP Claims

| Claim | Evidence |
|---|---|
| Explainer type: TreeExplainer | `shap_asset_inventory.json` |
| Background samples: 1000 | `shap_asset_inventory.json` |
| Transformed width: 49 | `shap_asset_inventory.json` |
| SHAP additivity: 100% | `shap_additivity_validation.json` |

---

## 7. Performance Numbers

From `feature_3_1_benchmark_results.json` (local Python 3.13.7):

| Operation | Mean |
|---|---|
| Model load | 928 ms |
| Warm single inference | 15.6 ms |

**No SLA** — explicitly documented.

---

## 8. Blockers & Warnings

**Blocker:** F37-B01 (no live Python env — pytest blocked)
**Warnings:** None at phase level.

**Next phase: MAY_BEGIN**
