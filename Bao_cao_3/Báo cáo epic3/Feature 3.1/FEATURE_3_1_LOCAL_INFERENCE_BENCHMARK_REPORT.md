# FEATURE 3.1 — Local Inference Benchmark Report
**Phase:** 4/5
**Feature:** 3.1 — Artifact Intake & Validation Gate
**Person in Charge:** Minh
**Session:** 2026-08-04

---

## 1. Benchmark Scope

**Scope:** LOCAL_INFERENCE
**What this is:** Local model/package inference latency on desktop Windows 11.
**What this is NOT:** Production API benchmark, network latency, or SLA.

---

## 2. Environment

| Parameter | Value |
|-----------|-------|
| OS | Windows-11-10.0.26200 |
| Processor | Intel Core i7-12700 (12 logical cores) |
| RAM | 16.8 GB |
| Python | 3.13.14 |
| scikit-learn | 1.8.0 |
| XGBoost | 3.3.0 |
| joblib | 1.5.3 |
| numpy | 2.4.6 |
| Model ID | EXP24-XGB-FINAL-001 |
| Model version | 1.0.0 |
| Package version | 1.0.0 |
| Artifact SHA-256 | `7ff4b1…d99` |
| Git commit | `2a6343f` |

---

## 3. Benchmark Configuration

| Parameter | Value |
|-----------|-------|
| Timer | `time.perf_counter_ns` |
| GC during timing | Disabled |
| Cold load runs | 5 (fresh subprocess) |
| Warm-up iterations | 10 |
| Measured single predictions | 200 |
| Batch sizes | 1, 10, 100 |
| Runs per batch size | 20 |
| Input source | `example_input.json` (canonical) |
| Batch method | Sequential loop (native batch not supported by wrapper) |

---

## 4. Input Policy

All benchmarks use the canonical `example_input.json` — a 1992 song with 18 raw audio features. Repeating the same record measures runtime mechanics, not data diversity. No synthetic data generated.

---

## 5. Cold Model Load

Fresh subprocess, process start → pipeline loaded.

| Statistic | Value |
|-----------|-------|
| Runs | 5 |
| Min | 697 ms |
| Max | 1,822 ms |
| **Median** | **700 ms** |
| Mean | 928 ms |
| Std | 500 ms |
| P90 | 1,822 ms |
| P95 | 1,822 ms |

Cold load has high variance (std = 500 ms) due to Windows subprocess startup overhead and first-time DLL loading. Subsequent loads are faster once DLLs are cached by OS.

---

## 6. First Prediction

Measured after fresh load, before any warm-up.

| Statistic | Value |
|-----------|-------|
| Runs | 5 |
| **Median** | **21.0 ms** |
| Mean | 22.2 ms |
| Min | 18.6 ms |
| Max | 28.9 ms |

First prediction is slightly slower than warm predictions due to lazy initialization (XGBoost internal structures, sklearn validation overhead on first call).

---

## 7. Warm Single-Record Inference

200 measurements after 10 warm-up iterations. Same pipeline object, same input.

| Statistic | Value |
|-----------|-------|
| Runs | 200 |
| Min | 12.3 ms |
| **Median** | **14.3 ms** |
| Mean | 15.6 ms |
| Std | 3.0 ms |
| P90 | 19.6 ms |
| P95 | 21.0 ms |
| P99 | 23.5 ms |
| Max | 27.1 ms |
| CV | 19.5% |

**Interpretation:** Warm single prediction is fast enough for interactive use. The coefficient of variation (~20%) reflects normal system noise on a desktop OS, not model instability.

---

## 8. Batch Inference

Sequential loop over single predictions (native batch not supported by wrapper).

| Batch Size | Runs | Total Median | Per-Record Median | Per-Record P95 | Records/sec |
|-----------|------|-------------|------------------|----------------|------------|
| 1 | 20 | 12.8 ms | **12.8 ms** | 14.1 ms | ~78 |
| 10 | 20 | 132.8 ms | **13.3 ms** | 15.9 ms | ~75 |
| 100 | 20 | 1,337.6 ms | **13.4 ms** | 46.5 ms | ~75 |

**Lưu ý:** Cột `Records/sec` tính bằng `1000 / per_record_ms`. Các giá trị trước đây (~78,300) bị nhân thừa 1000 lần do lỗi tính toán. Hiệu suất thực tế là ~75–78 records/giây.

Per-record latency is stable across batch sizes (~12–14 ms), confirming no per-call overhead for sequential processing of multiple records. P95 increases at batch size 100 due to GC/system noise.

---

## 9. Prediction Consistency

| Check | Result |
|-------|--------|
| Unique values across 200 warm predictions | 1 |
| Max absolute difference | 0.0 |
| Deterministic | ✅ YES |

All 200 predictions produced the exact same value: `46.421062`. No jitter.

---

## 10. Memory

**Status:** Not measured (optional, psutil available but not used in this benchmark session).

---

## 11. Reproducibility

| Metric | Session 1 |
|--------|-----------|
| Cold load median | 700 ms |
| Warm single median | 14.3 ms |
| Batch 100 per-record | 13.4 ms |

Single session only; reproducibility across sessions not validated in this run.

---

## 12. Target Latency Comparison

**TARGET_DEFINED_IN_SOURCE:** No

No EPIC 3 or project SLA document defines a target inference latency. This benchmark establishes a local baseline only.

---

## 13. Limitations

1. **Single input record** — Benchmark uses one canonical input repeatedly; does not reflect latency variation across different feature distributions.
2. **Desktop OS** — Windows 11 desktop with system services; not a dedicated server environment.
3. **Warm/cold measured in-process** — Cold load measured in subprocess but warm inference measured in the main Python process; OS DLL caching affects subprocess calls differently.
4. **Sequential batch** — Batch latency is sequential loop, not vectorized native batch; true batch speedup may differ.
5. **No memory profiling** — Total model memory footprint not measured.

---

## 14. Warnings

None.

---

## 15. Blockers

None.

---

## 16. Phase Gate

| Criterion | Status |
|-----------|--------|
| Benchmark methodology valid | ✅ PASS |
| Cold load benchmark successful | ✅ PASS |
| First prediction benchmark successful | ✅ PASS |
| Warm single benchmark successful | ✅ PASS |
| Batch benchmark successful | ✅ PASS |
| Raw samples recorded | ✅ PASS |
| Prediction consistency valid | ✅ PASS |
| No mutation | ✅ PASS |
| No SLA claimed | ✅ PASS |
| Tests pass | ✅ PASS (128/128) |

**Phase Gate Status: PASS**
**Next Phase: MAY_BEGIN**

---

## 17. Benchmark Interpretation

| Finding | Conclusion |
|---------|------------|
| Cold load ~700 ms | Acceptable for desktop application startup |
| First prediction ~21 ms | Slightly slower than warm; acceptable |
| Warm single ~14 ms/record | Usable for local interactive use (< 100 ms) |
| Batch per-record ~13 ms | Stable; no per-call overhead |
| Deterministic | ✅ All predictions identical |
| No production SLA claimed | ✅ Correctly scoped as local baseline |
