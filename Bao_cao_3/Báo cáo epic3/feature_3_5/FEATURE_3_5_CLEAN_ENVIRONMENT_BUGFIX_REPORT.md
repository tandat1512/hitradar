# Feature 3.5 — Clean Environment & Bug Fix Report
## Phase 4 — Reproducibility, Dependency Audit, Bug Triage & Hotfix

**Feature:** 3.5 — Integration & End-to-End Testing
**Phase:** 4 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (no live Python environment)

---

## 1. Clean Environment Definition

| Field | Value |
|---|---|
| Method | ISOLATED_VENV |
| Venv creation | `python -m venv --system-site-packages false <path>` |
| Constraint | No packages inherited from active project venv |
| Source snapshot | WORKING_TREE (uncommitted files used) |
| Git operations | NOT USED — no clean/reset/checkout/restore |
| Live test | PENDING — requires Python interpreter |

---

## 2. Dependency Declaration Audit

### Backend (5.UNG_DUNG/5.1.backend_api/requirements.txt)

| Package | Declared | Purpose |
|---|---|---|
| fastapi | ✅ ≥0.110.0 | Web framework |
| uvicorn | ✅ ≥0.30.0 | ASGI server |
| pydantic | ✅ ≥2.0.0 | Data validation |
| joblib | ✅ ≥1.4.0 | Model loading |
| scikit-learn | ✅ ≥1.5.0 | ML runtime |
| xgboost | ✅ ≥2.0.0 | Model |
| numpy | ✅ ≥1.26.0 | Numerical |
| pandas | ✅ ≥2.0.0 | Data |
| shap | ✅ ≥0.45.0 | Explainability |
| httpx | ⚠️ MISSING (added FIX_APPLIED) | Testing |

### Frontend (epic3/feature_3_3/frontend/)

| Package | Declared | Status |
|---|---|---|
| streamlit | ❌ NO requirements.txt | BUG F35-BUG-003 |
| httpx | ❌ NO requirements.txt | BUG F35-BUG-003 |

### Summary

- Backend: All runtime packages declared ✅. httpx added for testing completeness.
- Frontend: No requirements.txt ⚠️ — BUG F35-BUG-003.

---

## 3. Portability Audit

| Check | Result |
|---|---|
| Hardcoded `<PROJECT_ROOT> paths | NOT FOUND ✅ |
| Hardcoded `<PROJECT_ROOT> paths | NOT FOUND ✅ |
| Hardcoded `Users\` paths | NOT FOUND ✅ |
| Absolute repo paths in code | NOT FOUND ✅ |
| Path resolution | Relative via `Path(__file__)` ✅ |
| Configurable ports | `PORT` / `STREAMLIT_SERVER_PORT` ✅ |
| Machine-specific blocking paths | **0** ✅ |

---

## 4. Bug Registry

| Bug ID | Severity | Scenario | Root Cause | Fix | Status |
|---|---|---|---|---|---|
| F35-BUG-001 | **BLOCKER** | No live Python env — E2E blocked | No Python interpreter available | Run in live env | NOT_FIXABLE |
| F35-BUG-002 | LOW | httpx missing from backend requirements | httpx is testing dep; declared in epic3 but not 5.UNG_DUNG | Add httpx>=0.27.0 to requirements.txt | **FIX_APPLIED** ✅ |
| F35-BUG-003 | MEDIUM | No requirements.txt in frontend | Missing declaration | Create requirements.txt | PENDING |

---

## 5. Hotfix: F35-BUG-002

**Bug:** `httpx` not declared in `5.UNG_DUNG/5.1.backend_api/requirements.txt`
**Root cause:** httpx is a testing dependency; backend runtime doesn't need it. But for full test coverage in a clean environment, httpx should be declared.
**Fix:** Added `httpx>=0.27.0` to `5.UNG_DUNG/5.1.backend_api/requirements.txt`
**Files modified:** `5.UNG_DUNG/5.1.backend_api/requirements.txt`
**No model artifacts modified:** ✅
**No source dataset modified:** ✅

---

## 6. Pending Fix: F35-BUG-003

**Bug:** No `requirements.txt` in `epic3/feature_3_3/frontend/`
**Root cause:** Frontend dependencies (streamlit, httpx) not declared in frontend directory
**Fix required:** Create `requirements.txt` with:
```
streamlit>=1.30.0
httpx>=0.27.0
```
**Status:** PENDING — requires file creation

---

## 7. Source Immutability

| Item | Modified? |
|---|---|
| `artifacts/epic2/pipeline/full_inference_pipeline.joblib` | NOT_MODIFIED ✅ |
| `7.ML/7.4.feature_transformers/ohe_and_scaler.joblib` | NOT_MODIFIED ✅ |
| `7.ML/7.9.explainability/` | NO ✅ |
| `5.DATA/processed/ml_ready_dataset.csv` | NO ✅ |
| Backend code | httpx added only ✅ |
| Frontend code | NO ✅ |

---

## 8. Regression Test Map

| Bug ID | Regression Test | Status |
|---|---|---|
| F35-BUG-001 | Backend health check → 200 | PENDING |
| F35-BUG-002 | `pip install httpx` succeeds after `pip install -r requirements.txt` | PENDING |
| F35-BUG-003 | Fresh venv: `pip install -r requirements.txt` in frontend dir succeeds | PENDING |

---

## 9. Path Forward

To complete Phase 4 and unblock Phase 5:

1. Fix F35-BUG-003: Create `requirements.txt` in `epic3/feature_3_3/frontend/`
2. Create fresh venv: `python -m venv .venv && source .venv/bin/activate`
3. Install backend: `pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt`
4. Install frontend: `pip install -r epic3/feature_3_3/frontend/requirements.txt`
5. Start backend: `cd 5.UNG_DUNG/5.1.backend_api && python -m uvicorn api:app --port 8000`
6. Start frontend: `cd epic3/feature_3_3/frontend && streamlit run app.py`
7. Run clean predict smoke with canonical input
8. Rerun Phase 1–3 critical tests
