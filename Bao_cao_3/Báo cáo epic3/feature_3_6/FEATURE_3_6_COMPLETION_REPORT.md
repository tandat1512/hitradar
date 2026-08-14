# Feature 3.6 — Completion Report
## Performance, Reliability & Demo Backup

**Feature:** 3.6 · **Phase:** 5/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-07
**Decision:** NOT_CLOSED (needs live acceptance run) · **Feature 3.7 Gate:** BLOCKED

---

## What Was Completed

### Tasks 3.6.1–3.6.5 — Performance (Phases 1–2)
- Baseline methodology + artifacts (BLOCKED for live numbers).
- **Phase 2 là evidence-driven design audit**, không phải implementation sprint: 5 optimization candidates → 4 ALREADY_OPTIMIZED (đã tối ưu từ trước), 1 NOT_JUSTIFIED (không đủ baseline để prove impact). "0 code changes" = kết quả đúng, không phải gap — không sửa code đã tối ưu rồi.
- Cache correctness: key contract, invalidation (4 cases), mutation safety, memory summary, no-refit audit (0 fit calls).

### Tasks 3.6.6–3.6.8 — Startup Automation (Phase 3)
- `scripts/run_backend.py`, `scripts/run_frontend.py`, `scripts/run_all.py` + shared `_common.py`.
- Port conflict → refuse + exit 2 (never kills). run_all waits for **real /health (model_loaded=true), no fixed sleep**. Failure handling prevents orphans. Cleanup = own children only.

### Tasks 3.6.9–3.6.11 — Demo Backup (Phase 4)
- Screenshot inventory (7) + manifest — honest REQUIRES_LIVE_CAPTURE.
- Video shot list (7 scenes) + manifest — MANUAL_RECORDING_REQUIRED (no fake mp4).
- Offline demo mode contract — explicit labeling, precomputed-only evidence, Explain/What-if honestly NOT_AVAILABLE, live recovery.

### Tasks 3.6.12–3.6.13 — Operations (Phase 5)
- `demo_reliability_checklist.md` (9 sections).
- `DEMO_RUNBOOK_FEATURE_3_6.md` (18 sections; actual commands, ports, env, fallback).
- Traceability validated: env names match actual Settings/.env.example, ports consistent (8000/8501, configurable), commands documented with exact invocation.

## What Remains (Blocked)

1. Live API/page re-benchmark (baseline + final) → performance comparison.
2. Live smokes: run_backend, run_frontend, run_all, port conflict, offline fallback.
3. Full pytest suite (test_feature_3_6_*.py).
4. Screenshot capture + video recording.
5. Live correctness guard (6 endpoints + dashboard aggregates).

All blocked by **F36-B01: no live Python environment**.

## Immutability

Training/tuning/refit: NO. Model/schemas/SHAP/dataset: NOT MODIFIED. Write scope: additive (scripts/, demo/, reports).

## Summary

Feature 3.6's engineering deliverables are complete and honest. Closure requires executing the acceptance suite in a live environment. The single root blocker must be resolved before Feature 3.7 can begin.
