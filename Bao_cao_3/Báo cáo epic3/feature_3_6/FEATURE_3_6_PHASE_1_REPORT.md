# Feature 3.6 — Phase 1 Report
## Baseline Performance Benchmark

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 1 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED

---

## PHASE 1 EVIDENCE

### Prerequisite — Feature 3.5

| Check | Required | Actual | Satisfied |
|---|---|---|---|
| Predict real E2E valid | YES | false (live BLOCKED) | ❌ |
| FastAPI startup valid | YES | false | ❌ |
| Streamlit startup valid | YES | false | ❌ |
| Model artifacts unchanged | YES | true | ✅ |
| Training/refit = false | YES | true | ✅ |
| Remaining BLOCKER bugs = 0 | YES | 1 (F35-BUG-001 env) | ❌ |
| Remaining HIGH bugs = 0 | YES | 0 | ✅ |

**Decision: PHASE_1_BLOCKED** — benchmarking a system whose functional E2E has not been validated would produce an invalid baseline.

### Deliverables Created (17 artifacts)

| Artifact | Purpose | Status |
|---|---|---|
| feature_3_5_to_feature_3_6_gate_validation.json | Prerequisite gate | BLOCKED |
| feature_3_6_phase_1_session.json | Session record | ✅ |
| feature_3_6_benchmark_environment.json | Env snapshot design | ✅ |
| feature_3_6_benchmark_process_context.json | Process isolation | ✅ |
| feature_3_6_benchmark_input_contract.json | Canonical input contract | ✅ |
| feature_3_6_backend_startup_benchmark.csv | Startup benchmark | BLOCKED |
| feature_3_6_api_latency_samples.csv | Latency samples | BLOCKED |
| feature_3_6_api_latency_baseline.json | Latency statistics | BLOCKED |
| feature_3_6_model_load_baseline.json | Model load count | ✅ (source) |
| feature_3_6_artifact_read_baseline.json | Artifact reads | ✅ (source) |
| feature_3_6_streamlit_page_benchmark_registry.json | Page inventory | ✅ |
| feature_3_6_frontend_startup_benchmark.csv | Frontend startup | BLOCKED |
| feature_3_6_streamlit_page_latency_samples.csv | Page samples | BLOCKED |
| feature_3_6_streamlit_page_latency_baseline.json | Page statistics | BLOCKED |
| feature_3_6_dashboard_load_baseline.json | Dashboard caching | ✅ (source) |
| feature_3_6_baseline_bottlenecks.json | Bottleneck classification | ✅ (source) |
| feature_3_6_baseline_correctness_guard.json | Correctness guard | BLOCKED |
| feature_3_6_phase_1_source_immutability.json | Immutability | ✅ |
| feature_3_6_phase_1_gate.json | Phase gate | FAIL |

### Key Source-Audit Findings

1. **Model loading: ALREADY_OPTIMIZED candidate** — eager load in lifespan, singleton cache, 1 load per backend lifecycle, 0 reloads during requests.
2. **Dashboard data: ALREADY_OPTIMIZED candidate** — Feature 3.4 uses `st.cache_data` keyed by source SHA-256; 169,681-row CSV loaded once per Streamlit cache lifecycle.
3. **SHAP explainer: cached once globally**; per-request SHAP computation inherent (MEDIUM).
4. **model_metrics.json read per /model-info** — minor repeated artifact read (LOW priority Phase 2 candidate).
5. **Page inventory:** 7 real pages confirmed (Home, Predict, Explain, What-if, Trends, Model Info, Limitations).

### Immutability

- Model/schemas/SHAP/trend dataset: NOT_MODIFIED
- Production code: NOT modified
- Training/refit: not executed
- Live hash before/after: CAPTURE_LIVE when benchmark runs

---

## Phase Gate

| Field | Value |
|---|---|
| Feature 3.5 gate valid | ❌ |
| Benchmark env recorded | ✅ (design) |
| API benchmark real HTTP | ❌ BLOCKED |
| API samples | 0 |
| Prediction mismatches | 0 (not measured) |
| Startup/first/warm baselines | ❌ BLOCKED |
| Model load baseline | ✅ resolved (source) |
| Artifact read baseline | ✅ resolved (source) |
| Page benchmark | ❌ BLOCKED |
| Dashboard load baseline | ✅ resolved (source) |
| Bottlenecks identified | ✅ (source audit) |
| Training/refit/model/data modified | NO |
| Pytest | 0 collected (blocked) |
| Warnings | 4 |
| Blockers | 2 |

**Status: FAIL — BLOCKED**
**Next phase: BLOCKED**
