# Feature 3.6 — Phase 3 Report
## Reliable Demo Startup Automation

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 3 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED

---

## PHASE 3 EVIDENCE

### Canonical Commands (from source)

```
Backend:  cd 5.UNG_DUNG/5.1.backend_api && python -m uvicorn api:app --host 127.0.0.1 --port 8000
Frontend: cd epic3/feature_3_3/frontend && python -m streamlit run app.py --server.port 8501
```

### Deliverables (4 scripts + 7 artifacts)

| Deliverable | Status |
|---|---|
| scripts/_common.py (shared stdlib helpers) | ✅ CREATED |
| scripts/run_backend.py | ✅ CREATED |
| scripts/run_frontend.py | ✅ CREATED |
| scripts/run_all.py | ✅ CREATED |
| feature_3_6_phase_3_prerequisite_validation.json | ✅ |
| feature_3_6_startup_script_registry.json | ✅ |
| feature_3_6_startup_env_contract.json | ✅ |
| feature_3_6_process_ownership_validation.json | ✅ contract |
| feature_3_6_shutdown_validation.json | ✅ contract |
| feature_3_6_scripts_portability_validation.json | ✅ |
| feature_3_6_phase_3_gate.json | FAIL |

### Behavior Implemented (verified by source review)

- **run_backend:** artifact validation → port conflict (exit 2, no kill) → exact uvicorn → real /health polling (model_loaded=true) → Ctrl+C cleanup → exit code propagation.
- **run_frontend:** port conflict (exit 2) → backend-unreachable WARN (not fail) → streamlit start → /_stcore/health wait → cleanup.
- **run_all:** validate → start backend → **real /health readiness (NO fixed sleep)** → start frontend → print URLs → monitor → teardown own children only (frontend first, then backend; graceful → terminate → kill).
- **Failure handling:** backend exits before health → stop, exit 3; frontend exits → stop backend (no orphan); port occupied → exit 2 without killing anything.
- **Process ownership:** PIDs tracked; never kills foreign processes.
- **Portability:** 0 machine-specific paths; sys.executable; stdlib-only helper.

### Tests

Live pytest BLOCKED (no Python env). Spec'd files:

- test_feature_3_6_run_backend.py
- test_feature_3_6_run_backend_port_conflict.py
- test_feature_3_6_run_frontend.py
- test_feature_3_6_run_frontend_port_conflict.py
- test_feature_3_6_run_all.py
- test_feature_3_6_run_all_waits_for_health.py
- test_feature_3_6_run_all_backend_failure.py
- test_feature_3_6_run_all_health_timeout.py
- test_feature_3_6_run_all_frontend_failure.py
- test_feature_3_6_run_all_cleanup.py
- test_feature_3_6_process_ownership.py
- test_feature_3_6_scripts_no_absolute_dev_paths.py
- test_feature_3_6_startup_env_contract.py

### Immutability

Training: NO. Refit: NO. Model artifacts: NOT_MODIFIED. Source dataset: NOT_MODIFIED.

---

## Phase Gate

| Field | Value |
|---|---|
| run_backend complete | ✅ (start live ❌) |
| run_backend port handling | ✅ safe (exit 2, no kill) |
| run_frontend complete | ✅ (start live ❌) |
| run_frontend port handling | ✅ safe |
| run_all complete | ✅ (live ❌) |
| run_all waits for real /health | ✅ (no fixed sleep) |
| run_all failure handling | ✅ (no orphan) |
| Process ownership valid | ✅ design |
| Graceful shutdown valid | ✅ design |
| Orphan process count | 0 (by design; live ❌) |
| Machine-specific paths | 0 |
| Env contract complete | ✅ |
| Portability smoke | ❌ BLOCKED |
| Pytest | 0 collected (blocked) |
| Warnings | 2 |
| Blockers | 1 |

**Status: FAIL — BLOCKED**
**Next phase: BLOCKED**
