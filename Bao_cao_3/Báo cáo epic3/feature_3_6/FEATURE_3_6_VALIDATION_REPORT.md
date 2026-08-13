# Feature 3.6 — Validation Report
## Final Performance & Demo Reliability Acceptance

**Feature:** 3.6 · **Phase:** 5/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-07
**Status:** FAIL — NOT_CLOSED (single blocker: no live Python environment)

---

## 1. Phase 1–4 Audit

`feature_3_6_phase_audit.json` — all checkpoint claims backed by actual evidence artifacts.
**CHECKPOINT_EVIDENCE_MISMATCH: 0.** All BLOCKED statuses trace to the single root cause F36-B01.

## 2. Baseline

- API baseline: **BLOCKED** (no live env)
- Streamlit baseline: **BLOCKED** (no live env)
- Benchmark environment contract recorded at Phase 1 for exact reuse (same input, warm-up, count, method, config).

## 3. Optimization (Phase 2)

| Candidate | Decision |
|---|---|
| Model loading (3.6.3) | ALREADY_OPTIMIZED — eager lifespan load, 1/process, 0 reloads/request |
| Static metadata cache (3.6.4) | ALREADY_OPTIMIZED — PipelineLoader memoized |
| model_metrics.json | NOT_JUSTIFIED — no live baseline proving impact |
| Dashboard data cache (3.6.5) | ALREADY_OPTIMIZED — st.cache_data (2 layers) |
| Dashboard aggregation cache (3.6.5) | ALREADY_OPTIMIZED — param-keyed |

**Production code changed: 0.** No prediction/aggregate regression possible.

## 4. Startup Scripts (Phase 3)

| Script | Live run |
|---|---|
| scripts/run_backend.py | BLOCKED |
| scripts/run_frontend.py | BLOCKED |
| scripts/run_all.py | BLOCKED (real /health wait implemented — no fixed sleep) |

## 5. Backup & Offline (Phase 4)

- Screenshots: inventory complete, **0 captured (honest)**
- Video: **MANUAL_RECORDING_REQUIRED** (honest)
- Offline: contract complete — explicit labeling, precomputed-only Predict, **Explain/What-if NOT_AVAILABLE (no fabrication)**, live recovery defined

## 6. Phase 5 Deliverables

Checklist, runbook, env/port/command traceability, source immutability, architecture audit, write-scope audit, final validation results, evidence matrix, artifact manifest — all created.

## 7. Final Validation Results

`feature_3_6_final_validation_results.json` — 34 checks:

| Result | Count |
|---|---|
| PASS | 16 |
| FAIL (all BLOCKED by F36-B01) | 10 |
| Warnings | 3 |
| Blockers | 1 |

**Root blocker:** F36-B01 — no live Python environment → live benchmarks, smokes, pytest, capture impossible.

## 8. Conclusion

Every artifact that CAN be produced without a live environment is complete and honest (no fabricated media, numbers, or claims). Closure requires a live acceptance run.
