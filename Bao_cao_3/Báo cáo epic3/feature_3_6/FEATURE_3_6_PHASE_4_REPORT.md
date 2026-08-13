# Feature 3.6 — Phase 4 Report
## Demo Backup Package

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 4 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED

---

## PHASE 4 EVIDENCE

### Deliverables (11 artifacts + 3 offline asset files + 1 screenshot dir)

| Deliverable | Status |
|---|---|
| feature_3_6_backup_capture_session.json | ✅ (capture BLOCKED) |
| feature_3_6_backup_screenshot_manifest.json | ✅ inventory (0 captured, honest) |
| demo/backup/screenshots/ (+ README) | ✅ canonical dir created |
| feature_3_6_demo_video_shot_list.md | ✅ 7 scenes |
| feature_3_6_backup_video_manifest.json | ✅ MANUAL_RECORDING_REQUIRED |
| feature_3_6_offline_demo_evidence_registry.json | ✅ (Predict validated; Explain/What-if NOT_AVAILABLE) |
| demo/offline/evidence/{example_input,example_output}.json | ✅ copies (originals untouched) |
| feature_3_6_offline_demo_mode_contract.json | ✅ full design |
| feature_3_6_backup_asset_safety_audit.json | ✅ 0 exposures |
| feature_3_6_phase_4_gate.json | FAIL |
| FEATURE_3_6_DEMO_BACKUP_OFFLINE_REPORT.md | ✅ |
| FEATURE_3_6_PHASE_4_REPORT.md | ✅ |

### Key Honesty Decisions

1. **No fake screenshots / video.** Environment cannot record → every entry recorded as `REQUIRES_LIVE_CAPTURE` / `MANUAL_RECORDING_REQUIRED` with null provenance. No fabricated `.mp4`, duration, or hash.
2. **Offline evidence = actual validated output only.** Predict uses the real canonical fixture (46.421062, model 1.0.0). Explain and What-If are **NOT_AVAILABLE** offline because no validated precomputed SHAP/delta exists — rendering invented values would violate the absolute-honesty rule.
3. **Offline mode is explicitly labeled** by contract: persistent prominent banner on all relevant pages; BLOCKER if a viewer cannot distinguish LIVE vs OFFLINE.
4. **Activation is explicit** (env override or user opt-in on connection/service-unavailable/timeout — never on 422 validation).
5. **No new model work:** 0 fit, 0 refit, model artifacts unmodified, dataset unmodified.

### Offline Scope (per page)

| Page | Offline | Behavior |
|---|---|---|
| Predict | ✅ precomputed scenario only | locked input; arbitrary input rejected |
| Explain | ❌ NOT_AVAILABLE | no dynamic SHAP |
| What-If | ❌ NOT_AVAILABLE | no local heuristics |
| Model Info | ✅ validated snapshot | labeled with version + time |
| Music Trends | ✅ local compute | labeled as local, not API snapshot |
| Home | ✅ static | + banner |

### Recovery

`/health` probe or Retry → "Switch back to Live" → `demo_mode = LIVE`. Never stuck offline.

---

## Phase Gate

| Field | Value |
|---|---|
| Screenshot inventory | ✅ complete (0 captured) |
| Screenshot provenance | ❌ (requires live capture) |
| Video status | MANUAL_RECORDING_REQUIRED |
| Video plan/manifest | ✅ complete |
| Offline evidence registry | ✅ complete |
| Offline mode implemented | ❌ (design complete; UI deferred to live env) |
| Offline mode explicitly labeled | ✅ (contract) |
| Offline arbitrary inference | false ✅ |
| Predict/Explain/What-if precomputed-only | ✅ (contract) |
| Live recovery | ✅ (contract) |
| Frontend model loads / SHAP computes | 0 / 0 |
| Backup secret exposures | 0 |
| Training / refit / artifacts modified | NO |
| Pytest | 0 collected (blocked) |
| Warnings | 2 |
| Blockers | 1 |

**Status: FAIL — BLOCKED**
**Next phase: BLOCKED**
