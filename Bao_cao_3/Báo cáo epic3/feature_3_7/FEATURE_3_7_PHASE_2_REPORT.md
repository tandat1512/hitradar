# Feature 3.7 — Phase 2 Report
## HOW_TO_RUN_APP.md & USER_MANUAL.md

**Feature:** 3.7 · **Phase:** 2/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09
**Status:** PASS_WITH_WARNINGS — MAY_BEGIN

---

## Phase 2 Evidence

```
HOW_TO_RUN_APP.md complete:               YES ✅
User Manual complete:                     YES ✅
Installation commands traceable:          YES ✅ (to actual scripts)
HOW_TO_RUN walkthrough valid:            BLOCKED — F37-B01 (structurally OK)
Machine-specific runtime paths:            0 ✅
Actual Streamlit pages documented:        YES ✅ (7 pages)
Nonexistent pages documented:             0 ✅
Prediction as probability:                NO ✅
SHAP causal claims:                      0 ✅
What-If causal claims:                   0 ✅
Dashboard overgeneralizations:           0 ✅
Offline mode: precomputed fallback:      YES ✅
Broken doc links:                         0 ✅
Implementation mismatches:               0 ✅ (35 checks OK)
Production code modified:                NO ✅
Next phase:                              MAY_BEGIN
```

---

## 1. Feature 3.6 Gate

Feature 3.6: FAIL — NOT_CLOSED (F36-B01).
Feature 3.7 gate: **DOCUMENTATION_MAY_BEGIN_WITH_UPSTREAM_WARNINGS**.

## 2. Source Validation

All commands, ports, pages, fields, and behavior extracted from actual source files:
- Scripts: `run_all.py`, `run_backend.py`, `run_frontend.py`, `_common.py`
- Frontend: 7 actual page files + navigation registry
- Schema: `input_schema.json` (18 fields)
- Config: `config.py`

## 3. HOW_TO_RUN_APP.md

**Created at:** `HOW_TO_RUN_APP.md` (repository root).

Commands extracted from actual scripts — not copied from old reports:
- `python scripts/run_all.py` (full stack)
- `python scripts/run_backend.py` (backend only)
- `python scripts/run_frontend.py` (frontend only)
- Port defaults: 8000 / 8501 (verified from source)
- Health semantics: polls `GET /health` until `model_loaded==true` (no fixed sleep)
- Port conflict: exits code 2, never kills (verified from `_common.py`)
- Machine-specific paths: 0

## 4. USER_MANUAL.md

**Created at:** `USER_MANUAL.md` (repository root).

Pages documented from actual page files:
- All 7 pages from navigation registry
- 18 input fields with exact ranges from `input_schema.json`
- Output described as regression score (0–100) — no probability language
- SHAP: causal claim count = 0
- What-If: causal claim count = 0
- Music Trends: "available dataset shows" not "all music"

## 5. Offline Mode Documentation

Both documents describe offline mode correctly:
- **What it is:** precomputed validated demonstration
- **What it is not:** backup model, live inference
- SHAP / What-If: correctly marked NOT AVAILABLE offline
- Visible banner required on every page (per Feature 3.6 contract)

## 6. Blockers & Warnings

**Blockers:** F37-B01 (no live Python env).
**Warnings:** F37-W04 (walkthrough not live-executed), F37-W01 (2 intentional placeholders).

## 7. Artifacts Created

Phase 2 validation artifacts in `feature_3_7/validation/`:
`phase_2_source_validation.json`, `how_to_run_command_matrix.csv`, `user_manual_ui_inventory.json`, `user_manual_prediction_terminology.json`, `user_docs_consistency_matrix.csv`, `phase_2_link_validation.json`, `phase_2_gate.json`.

## 8. Next Steps for Phase 3

1. Create `API_DOCUMENTATION.md` (link already in README/HOW_TO_RUN)
2. Resolve README → API_DOCUMENTATION broken link (currently INTENTIONAL placeholder)
