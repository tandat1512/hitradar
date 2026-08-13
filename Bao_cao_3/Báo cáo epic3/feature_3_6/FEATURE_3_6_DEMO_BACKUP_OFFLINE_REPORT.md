# Feature 3.6 — Demo Backup & Offline Mode Report
## Phase 4 — Screenshots / Video / Offline Demo Mode

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 4 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (assets require live env; no fabricated media)

---

## The Three Backup Tiers

| Tier | What | Status |
|---|---|---|
| **TIER 1** | LIVE DEMO (normal API flow) | design complete; live run BLOCKED |
| **TIER 2** | OFFLINE DEMO MODE (precomputed validated evidence, explicitly labeled) | contract complete; implementation deferred to live env |
| **TIER 3** | STATIC BACKUP MEDIA (screenshots / video) | inventory + shot list complete; capture requires live env |

**Purpose is NOT to hide errors** — it is to prove flows ran successfully before, if the live API fails during a presentation.

---

## 1. Backup Capture Session

`feature_3_6_backup_capture_session.json` defines the run metadata contract (git commit, model version 1.0.0, canonical scenario IDs) for all captures. **Actual capture: BLOCKED** (no live Python env).

## 2. Screenshot Inventory

7 required screenshots defined in `feature_3_6_backup_screenshot_manifest.json`:
Home · Predict result · SHAP Explanation · What-If · Music Trends · Model Info · Responsible Use.

Canonical directory created: `demo/backup/screenshots/` (with README).
**Captured: 0** — every entry honestly recorded as `REQUIRES_LIVE_CAPTURE` with null provenance (no fabricated capture time / request_id / hash).

Quality rules: readable, no terminal overlays, no personal paths/secrets, no misleading crops, predictions unaltered. Explain page is never faked.

## 3. Video

- **Shot list complete:** `feature_3_6_demo_video_shot_list.md` — 7 scenes (Home → Predict → Explain → What-if → Trends → Model Info → Responsible Use), ~3.5 min, per-scene expected visible result + narration cue + backup purpose.
- **Manifest:** `feature_3_6_backup_video_manifest.json` → `status: MANUAL_RECORDING_REQUIRED`. No fake `.mp4`, no guessed duration/hash.

## 4. Offline Evidence Registry

`feature_3_6_offline_demo_evidence_registry.json` — only validated precomputed outputs:

| Evidence | Status | Note |
|---|---|---|
| Predict (canonical example → 46.421062) | **VALIDATED** | real E2E canonical fixture |
| Explain | **NOT_AVAILABLE** | no validated SHAP values — fabricating is forbidden |
| What-If | **NOT_AVAILABLE** | no validated delta — computing locally is forbidden |
| Model Info | **VALIDATED_SNAPSHOT** | static metadata JSONs |
| Music Trends | **LIVE_LOCAL_COMPUTE** | local dataset, labeled as local |

Copies placed in `demo/offline/evidence/` (originals in `artifacts/epic2/examples/` untouched). SHA-256 recorded as PENDING_LIVE.

## 5. Offline Mode Contract

`feature_3_6_offline_demo_mode_contract.json`:
- **Activation:** explicit only — `OFFLINE_DEMO_MODE=true` or user opt-in via UI offer on `APIConnectionError` / `APIServiceUnavailableError` / repeated `APITimeoutError`. **Never** on 422 validation.
- **Banner (all relevant pages, persistent):** "OFFLINE DEMO MODE — Precomputed validated result. No live model inference is being performed."
- **Predict:** locked to prepared scenario; arbitrary input → "Offline mode supports only prepared demo scenarios."
- **Explain / What-If offline:** NOT_AVAILABLE (no fabricated values).
- **Recovery:** health probe / Retry → "Switch back to Live" → mode=LIVE; never stuck offline.
- **Session state:** `demo_mode` ∈ {LIVE, OFFLINE}.

**Frontend guards:** 0 model loads, 0 SHAP computes in frontend; offline computes no inference.

## 6. Safety Audit

`feature_3_6_backup_asset_safety_audit.json` — secrets in backup assets: **0**; no auth headers, personal env values, home paths, or credentials. Capture/recording quality rules documented.

## 7. Validation Status

Live pytest + screenshot capture + offline UI tests: **BLOCKED** (no Python env). Design/contract/evidence artifacts: complete.

## 8. Warnings / Blockers

**Warnings:** F36-W09 (assets not captured — honest REQUIRES_LIVE_CAPTURE/MANUAL_RECORDING_REQUIRED), F36-W10 (offline mode designed, implementation deferred to live env).
**Blockers:** F36-B01 (no live Python environment).

**Gate: FAIL — BLOCKED**
