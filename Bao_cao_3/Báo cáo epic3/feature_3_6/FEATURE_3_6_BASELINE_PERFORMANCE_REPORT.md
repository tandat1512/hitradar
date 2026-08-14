# Feature 3.6 — Baseline Performance Report
## Phase 1 — API Prediction Latency & Streamlit Page Load Benchmark

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 1 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (prerequisite: Feature 3.5 NOT_CLOSED, no live Python env)

---

## 1. Environment

| Component | Value |
|---|---|
| OS | Windows 11 Home Single Language 10.0.26200 |
| Architecture | amd64 (capture live) |
| CPU / RAM | CAPTURE_LIVE |
| Python | CAPTURE_LIVE |
| Backend | FastAPI ≥0.110, uvicorn ≥0.30, port 8000 |
| Frontend | Streamlit ≥1.30, port 8501 |
| HTTP client | httpx ≥0.27 |
| Model artifact | artifacts/epic2/pipeline/full_inference_pipeline.joblib |
| Trend dataset | 5.DATA/processed/ml_ready_dataset.csv (169,681 rows) |

**Note:** These measurements characterize this local test environment. Not claimed transferable.

---

## 2. Methodology

- **Transport:** actual local HTTP (httpx) against real FastAPI process — NOT TestClient
- **Clock:** `time.perf_counter()` (monotonic high-resolution)
- **Warm-up:** 5 requests before warm summary (excluded from statistics)
- **Samples:** 30–100 sequential requests
- **Correctness guard:** every request validated against canonical 46.421062 ± 0.001
- **Metrics separated:** (A) application startup, (B) first prediction, (C) warm prediction — never mixed

### Lifecycle finding (from source audit)

Model is loaded **eagerly at startup** in `lifespan` (`api.py:47-51`). First `/predict` is therefore **WARM-MODEL_FIRST-REQUEST**, not cold-model.

---

## 3. Startup Benchmark

| Run | startup_ms | health | model_ready | cleanup |
|---|---|---|---|---|
| RUN-001 | PENDING | PENDING | PENDING | PENDING |
| RUN-002 | PENDING | PENDING | PENDING | PENDING |
| RUN-003 | PENDING | PENDING | PENDING | PENDING |

*Live measurement blocked. Method: start process → poll /health (no fixed sleep) → record first healthy time → stop → cleanup.*

---

## 4. First Prediction

Definition: backend ready → first actual HTTP POST /predict → complete response.

**PENDING** — requires live backend.

---

## 5. Warm Prediction

| Metric | Value |
|---|---|
| Count | PENDING |
| p50 (median) | PENDING |
| p95 | PENDING |
| min / max | PENDING |
| failure rate | PENDING |

---

## 6. Raw Sample Count

`feature_3_6_api_latency_samples.csv` — 1 placeholder row (BLOCKED). Live target: 30–100 samples.

---

## 7. p50/p95

PENDING — computed from raw CSV statistics when live run executes.

---

## 8. Failure Rate

PENDING — expected 0% at baseline.

---

## 9. Correctness Guard

| Guard | Value |
|---|---|
| Canonical prediction | 46.421062 |
| Tolerance | ±0.001 |
| Mismatch count | PENDING (expected 0) |
| Error count | PENDING (expected 0) |
| Model version mismatch | PENDING (expected 0) |

---

## 10. Model Load Baseline (SOURCE-RESOLVED)

| Field | Value |
|---|---|
| Load point | eager at startup (lifespan) |
| Cache | PipelineLoader singleton (`_pipeline`) |
| Loads per backend lifecycle | **1** |
| Reloads during prediction requests | **0** |
| Classification | **ALREADY_OPTIMIZED candidate** |
| SHAP explainer | lazy, built once, cached globally |

---

## 11. Artifact Load Baseline (SOURCE-RESOLVED)

| Artifact | Frequency | Cached | Classification |
|---|---|---|---|
| full_inference_pipeline.joblib | 1/lifecycle | ✅ | ALREADY_OPTIMIZED |
| schemas/input_schema.json | 1/lifecycle | ✅ | ALREADY_OPTIMIZED |
| schemas/selected_features.json | 1/lifecycle | ✅ | ALREADY_OPTIMIZED |
| metadata/*.json | 1/lifecycle | ✅ | ALREADY_OPTIMIZED |
| model_metrics.json | **per /model-info** | ❌ | MINOR (LOW priority candidate) |

---

## 12. Streamlit Startup

| Run | startup_ms | app_ready | cleanup |
|---|---|---|---|
| RUN-001 | PENDING | PENDING | PENDING |
| RUN-002 | PENDING | PENDING | PENDING |
| RUN-003 | PENDING | PENDING | PENDING |

*Live measurement blocked.*

---

## 13. Page Results

| Page | Cold median | Warm median | p95 | Status |
|---|---|---|---|---|
| HOME | PENDING | PENDING | PENDING | BLOCKED |
| PREDICT | PENDING | PENDING | PENDING | BLOCKED |
| MUSIC_TRENDS | PENDING | PENDING | PENDING | BLOCKED |
| MODEL_INFO | PENDING | PENDING | PENDING | BLOCKED |
| EXPLAIN | PENDING | PENDING | PENDING | BLOCKED |
| WHAT_IF | PENDING | PENDING | PENDING | BLOCKED |

*Measurement type: STREAMLIT_SCRIPT_EXECUTION (not browser DOM time — no browser instrumentation).*

---

## 14. Dashboard Results (SOURCE-RESOLVED)

| Stage | Cached? | Expected |
|---|---|---|
| Trend source load (169,681 rows) | ✅ st.cache_data (SHA-256 key) | once per Streamlit cache lifecycle |
| Aggregation (by_year/by_decade/popularity) | ✅ st.cache_data | once per param combination |
| Chart-data preparation | partial | measure live |
| Page execution | — | measure live |

**Dataset repeated-load status:** Dashboard uses cached path → **ALREADY_OPTIMIZED candidate**. Warm reruns cheap; first load may be hundreds of ms (measure live).

---

## 15. Bottlenecks (evidence-based)

| Category | Evidence | Confidence | Priority |
|---|---|---|---|
| SHAP_COMPUTATION | Per-request shap_values + fe/prep transform in /explain; first request pays TreeExplainer build | HIGH (structural) | MEDIUM |
| ARTIFACT_READING | model_metrics.json read per /model-info, uncached | HIGH (structural) | LOW |
| NETWORK_LOCAL_OVERHEAD | httpx loopback round-trip per action | MEDIUM | LOW |

### Already optimized (no change needed — WBS rule: ALREADY_OPTIMIZED with evidence)

| Category | Evidence |
|---|---|
| MODEL_LOADING | Eager load + singleton cache; 1 load/lifecycle |
| DATASET_LOADING | st.cache_data with source SHA-256 key |
| DASHBOARD_AGGREGATION | st.cache_data param-keyed |
| FRONTEND_SCRIPT_RERUN | All heavy work delegated to backend or cached loaders |

---

## 16. Optimization Candidates (Phase 2)

1. **Cache model_metrics.json** in PipelineLoader (first read → in-memory dict). LOW priority, tiny file.
2. **Measure, don't change:** SHAP per-request compute and local HTTP overhead are architecture-inherent.
3. **Confirm live** that dashboard first-load and first-explain are the only heavy cold paths.

Per WBS: if implementation is already optimal, record ALREADY_OPTIMIZED and provide evidence — **no gratuitous changes**.

---

## 17. Tests

Live pytest BLOCKED (no Python env). Spec'd harness files:

- test_feature_3_6_benchmark_environment.py
- test_feature_3_6_api_benchmark_harness.py
- test_feature_3_6_api_benchmark_real_http.py
- test_feature_3_6_api_benchmark_correctness.py
- test_feature_3_6_latency_statistics.py
- test_feature_3_6_model_load_observation.py
- test_feature_3_6_streamlit_benchmark_registry.py
- test_feature_3_6_page_benchmark_harness.py
- test_feature_3_6_dashboard_load_baseline.py
- test_feature_3_6_baseline_no_source_mutation.py

---

## 18. Warnings / Blockers

**Warnings**
- F36-W01: Feature 3.5 not closed — live E2E baseline invalid
- F36-W02: All latency statistics PENDING
- F36-W03: Hardware/software versions not captured live
- F36-W04: model_metrics.json per-request read (LOW)

**Blockers**
- F36-B01: F35-BUG-001 — no live Python environment
- F36-B02: No live backend/frontend processes to measure

---

## 19. Phase Gate

**Status: FAIL — BLOCKED**
**Next phase: BLOCKED**

Prerequisite per spec: Feature 3.5 must reach PASS before Feature 3.6 baseline is valid. Benchmark methodology, harness design, source-audit baselines, page registry, and bottleneck classification are complete and reproducible for Phase 2 re-run in a live environment.
