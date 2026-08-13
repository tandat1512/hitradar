# Feature 3.7 — Validation Report

**Feature:** 3.7 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09

---

## 1. Source-of-Truth Strategy

All documentation facts traced to canonical evidence files:

| Fact Type | Canonical Source |
|---|---|
| Model name/version/family | `artifacts/epic2/metadata/model_version.json` |
| Metrics | `epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_metrics_validation.json` |
| Feature counts | `artifacts/epic2/schemas/input_schema.json`, `selected_features.json`, `feature_names.json` |
| API paths/schemas | `5.UNG_DUNG/5.1.backend_api/openapi.json` |
| Architecture | `api.py`, `app.py`, `scripts/run_all.py` |
| Dashboard data | `epic3/feature_3_3/frontend/pages/4_Trends.py` |
| Performance | `epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json` |
| Limitations | `epic3/feature_3_3/frontend/pages/6_Limitations.py` |

No facts invented without source.

---

## 2. Cross-Document Consistency

24 facts checked across 5 documentation files.

| Category | Canonical | Docs | Consistent |
|---|---|---|---|
| Model name | EXP24-XGB-FINAL-001 | 5 | ✅ |
| Model version | 1.0.0 | 5 | ✅ |
| Model family | XGBoost | 5 | ✅ |
| Target | popularity 0-100 regression | 5 | ✅ |
| Raw features | 18 | 5 | ✅ |
| Selected features | 31 | 4 | ✅ |
| Transformed features | 49 | 1 | ✅ |
| MAE | 17.65 | 3 | ✅ |
| RMSE | 21.01 | 3 | ✅ |
| R² | 0.070 | 3 | ✅ |
| Backend port | 8000 | 5 | ✅ |
| Frontend port | 8501 | 5 | ✅ |
| API prefix | none | 2 | ✅ |
| Dataset year | 1922–2019 | 4 | ✅ (corrected Phase 5) |
| Offline mode | precomputed | 5 | ✅ |

2 inconsistencies corrected in Phase 5: README "1921-2020" → "1922-2019"; API docs placeholder metrics → actual values.

---

## 3. API Validation

All 6 endpoints match OpenAPI.

| Path | Method | Status Codes | Consistent |
|---|---|---|---|
| /health | GET | 200 | ✅ |
| /model-info | GET | 200, 503 | ✅ |
| /features | GET | 200, 503 | ✅ |
| /predict | POST | 200, 422, 503 | ✅ |
| /explain | POST | 200, 422, 503 | ✅ |
| /what-if | POST | 200, 422, 503 | ✅ |

No API prefix in use.

---

## 4. Claim Audit

All 10 unsupported claim categories: **0 found**.

---

## 5. Link Validation

19 internal Markdown links checked. **0 broken**.

---

## 6. Immutability

No training, no refit, no artifacts modified.

---

## 7. Warnings

| ID | Warning | Classification |
|---|---|---|
| F37-B01 | No Python env — live walkthrough blocked | Environment (not a doc defect) |
| F37-W01 | README broken links (was 4, all resolved) | Resolved |
| F37-W04 | HOW_TO_RUN walkthrough not live-executed | Environment |
| F37-W05 | API examples from E2E fixture | Informational |

---

## 8. Conclusion

Feature 3.7 documentation: **COMPLETE** and **ACCURATE**.
All cross-doc facts consistent. All unsupported claims = 0.
EPIC 3 Documentation Gate: **DOCUMENTATION_COMPLETE**.
