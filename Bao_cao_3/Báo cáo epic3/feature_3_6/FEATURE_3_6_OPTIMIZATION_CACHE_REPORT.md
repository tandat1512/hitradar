# Feature 3.6 — Optimization & Cache Report
## Phase 2 — Evidence-Driven Performance Optimization

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 2 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (prerequisite Phase 1 BLOCKED, no live Python env)

---

## 1. Baseline Bottlenecks (from Phase 1 source audit)

| Category | Evidence | Priority |
|---|---|---|
| SHAP_COMPUTATION | Per-request shap_values in /explain; first request pays TreeExplainer build (cached after) | MEDIUM |
| ARTIFACT_READING | model_metrics.json read per /model-info, uncached | LOW |
| NETWORK_LOCAL_OVERHEAD | httpx loopback round-trip per action | LOW |

**Already optimized (Phase 1):** model loading (eager once/lifecycle), dashboard data (st.cache_data + SHA-256), dashboard aggregation (param-keyed cache).

---

## 2. Optimization Decisions

| ID | Candidate | Decision | Evidence | Code changed? |
|---|---|---|---|---|
| OPT-001 | Model loading | **ALREADY_OPTIMIZED** | api.py lifespan eager load; PipelineLoader singleton; 1 load/process | NO |
| OPT-002 | Static metadata (schemas, versions, features) | **ALREADY_OPTIMIZED** | PipelineLoader memoizes _schemas/_selected_features/_metadata | NO |
| OPT-003 | model_metrics.json per /model-info | **NOT_JUSTIFIED** | Tiny file; no live baseline proving significance; no change without MEASURE | NO |
| OPT-004 | Dashboard data cache | **ALREADY_OPTIMIZED** | @st.cache_data page-level + F3.4 SHA-256-keyed layer | NO |
| OPT-005 | Dashboard aggregation cache | **ALREADY_OPTIMIZED** | Parameter-aware agg cache keys | NO |

**Outcome: 0 code changes.** Per WBS: "Không sửa code chỉ để task có diff" và "Nếu implementation hiện tại đã tối ưu đúng: KHÔNG sửa vô ích."

---

## 3. Model Loading — Before

- Type: FastAPI lifespan load + lazy singleton
- Call path: lifespan → `pipeline_loader.pipeline` → `_load_pipeline()` → `joblib.load(full_inference_pipeline.joblib)` + runtime patches → cached in `_pipeline`
- Loads per backend process: **1**
- Reloads during requests: **0**
- Per-request deserialization: none
- SHAP explainer: lazy global singleton, built once

## 4. Model Loading — After

**Unchanged (ALREADY_OPTIMIZED).** Matches the acceptable lifecycle: *application → model loaded once → shared read-only inference resource → many requests.*

Thread/process semantics: loaded once PER PROCESS. With multiple uvicorn workers each process loads its own copy (standard, correct).

---

## 5. Artifact Caching

| Artifact | Strategy | Frequency | Status |
|---|---|---|---|
| full_inference_pipeline.joblib | PipelineLoader singleton | 1/process | ALREADY_OPTIMIZED |
| schemas/input_schema.json | memoized | 1/process | ALREADY_OPTIMIZED |
| schemas/selected_features.json | memoized | 1/process | ALREADY_OPTIMIZED |
| metadata/*.json | memoized | 1/process | ALREADY_OPTIMIZED |
| model_metrics.json | none (per request) | per /model-info | NOT_JUSTIFIED (LOW) |
| SHAP artifacts | TreeExplainer cached once | 1/process | ALREADY_OPTIMIZED |
| Trend dataset CSV | st.cache_data (2 layers) | 1/session | ALREADY_OPTIMIZED |
| Aggregates | st.cache_data param-keyed | 1/(params) | ALREADY_OPTIMIZED |

Model resource cache is owned by the BACKEND (PipelineLoader), not Streamlit — correct per spec section 11. Frontend direct model loads: **0**.

---

## 6. Dashboard Cache

- **Page in use (4_Trends.py):** `@st.cache_data load_yearly_features(path)` — path-keyed, whole aggregation cached. Cold run: full CSV parse + 170k-row Python loop; warm: cached.
- **Feature 3.4 layer (dashboard_cache.py):** `load_trend_dataset_cached()` — SHA-256-keyed; `make_agg_cache_key()` — param-aware (feature, method, granularity, year bounds).

## 7. Cache Key

- Page layer: function + path string
- F3.4 layer: `path@sha8` (or mtime fallback) + params
- Both correct for an immutable demo dataset. Path-only keying does not detect content change at the same path — accepted, documented.

## 8. Invalidation

4 test cases defined: same source+params → reuse; changed params → new entry; changed source identity → no stale reuse; process restart → clear. **Live execution BLOCKED.**

## 9. Mutation Safety

- Backend: /features builds fresh FieldDescriptor objects from cached schema (defensive copy at boundary); metadata dicts read-only.
- Dashboard: F3.4 returns `.copy()`; page returns fresh dicts; no in-place mutation of cached structures.
- Design safe as sourced; live test BLOCKED.

## 10. Memory Summary

| Resource | Estimate | Note |
|---|---|---|
| Model pipeline in memory | ≈ joblib bytes + overhead | 1/backend process |
| Trend DataFrame (169,681×20) | ~30–60 MB | 1/session per layer |
| Cached aggregates | <1 MB | years×features |
| SHAP TreeExplainer | tens of MB | 1/backend process |
| Static JSON metadata | KB | negligible |

No multi-DataFrame cache explosion. No change needed.

---

## 11. Correctness Regression

**0 prediction regressions, 0 dashboard aggregate regressions** — no production code was modified. Live re-verification of all 6 endpoints + dashboard aggregates required at final smoke.

## 12. API Before/After

**BLOCKED** — no Phase 1 baseline, no optimization implemented. Comparison vacuous.

## 13. Streamlit Before/After

**BLOCKED** — same reason. Music Trends cold load is expected to be the slowest page (pure-Python 170k-row aggregation on first run, cached afterwards).

## 14. Regressions

None introduced (no code change). Existing observations documented: OPT-003 (model_metrics.json) and page-level aggregation implementation.

---

## 15. Tests

Live pytest BLOCKED. Spec'd files:

- test_feature_3_6_model_load_once.py
- test_feature_3_6_model_reload_on_restart.py
- test_feature_3_6_no_frontend_model_cache.py
- test_feature_3_6_artifact_cache_registry.py
- test_feature_3_6_cached_metadata_immutable.py
- test_feature_3_6_dashboard_cache.py
- test_feature_3_6_dashboard_cache_key.py
- test_feature_3_6_cache_invalidation.py
- test_feature_3_6_cache_mutation.py
- test_feature_3_6_cache_call_count.py
- test_feature_3_6_optimization_prediction_regression.py
- test_feature_3_6_optimization_dashboard_regression.py
- test_feature_3_6_optimization_no_refit.py
- test_feature_3_6_before_after_statistics.py

## 16. Warnings / Blockers

**Warnings:** F36-W02 (no live baseline), F36-W05 (model_metrics.json NOT_JUSTIFIED), F36-W06 (page aggregation pure-Python loop observation).
**Blockers:** F36-B01 (no live Python env), F36-B02 (no processes to test).

## 17. Gate

**Status: FAIL — BLOCKED**
**Next phase: BLOCKED**
