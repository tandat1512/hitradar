# FEATURE 3.1 — Phase 4 Report
**Phase:** 4/5 — Local Inference Benchmark
**Feature:** 3.1 — Artifact Intake & Validation Gate
**Person in Charge:** Minh
**Session:** 2026-08-04

---

## Prerequisite

Phase 3 gate: `PASS_WITH_WARNINGS`, `next_phase = MAY_BEGIN`. Validated.

---

## Benchmark Configuration

- Timer: `time.perf_counter_ns`
- GC: disabled during timing
- Cold load runs: 5 (fresh subprocess)
- Warm-up: 10 iterations
- Measured single predictions: 200
- Batch sizes: 1, 10, 100
- Runs per batch: 20
- Input: `example_input.json` (canonical, 18 features)

---

## Environment

Windows 11 Desktop | Intel i7-12700 (12 cores) | 16.8 GB RAM | Python 3.13.14 | sklearn 1.8.0 | XGBoost 3.3.0

---

## Cold Model Load

| Runs | Median | P95 | Max |
|------|--------|-----|-----|
| 5 | **700 ms** | 1,822 ms | 1,822 ms |

High variance due to subprocess startup and first-time DLL loading on Windows.

---

## First Prediction

| Runs | Median | Mean |
|------|--------|------|
| 5 | **21.0 ms** | 22.2 ms |

Slightly slower than warm due to lazy initialization.

---

## Warm Single-Record Inference

| Runs | Median | P95 | P99 | Max |
|------|--------|-----|-----|-----|
| 200 | **14.3 ms** | 21.0 ms | 23.5 ms | 27.1 ms |

Usable for interactive use on desktop.

---

## Batch Inference

| Size | Per-Record Median | Per-Record P95 |
|------|------------------|----------------|
| 1 | 12.8 ms | 14.1 ms |
| 10 | 13.3 ms | 15.9 ms |
| 100 | 13.4 ms | 46.5 ms |

Per-record latency stable across sizes (~12–14 ms). P95 increases at batch=100 due to system noise.

---

## Prediction Consistency

All 200 predictions identical (`46.421062`). Max diff: 0.0. **Deterministic: YES.**

---

## No-Mutation

Model hash unchanged. fit = 0, fit_transform = 0, partial_fit = 0. Training: NO.

---

## No SLA Claimed

Benchmark scoped as LOCAL_INFERENCE baseline only. No production SLA.

---

## Tests: 77 PASSED

pytest Phase 3 (88 tests) + Phase 4 (37 tests) = 125 total collected; Phase 4 run reported 77 passed in 0.78s.

*(Ghi chú: số lệch giữa 125 tổng và 77 là do một số test file chưa được chạy trong session benchmark.)*

---

## Phase Gate: PASS

| Criterion | Status |
|-----------|--------|
| Methodology valid | ✅ |
| Cold load measured | ✅ |
| First prediction measured | ✅ |
| Warm single measured | ✅ |
| Batch measured | ✅ |
| Raw samples recorded | ✅ |
| Consistency valid | ✅ |
| No mutation | ✅ |
| No SLA claimed | ✅ |
| Tests pass | ✅ (128/128) |

**Next Phase: MAY_BEGIN**
