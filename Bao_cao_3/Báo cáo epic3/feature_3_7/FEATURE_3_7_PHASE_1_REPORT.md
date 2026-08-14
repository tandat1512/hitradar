# Feature 3.7 — Phase 1 Report
## Documentation Foundation

**Feature:** 3.7 · **Phase:** 1/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09
**Status:** FAIL — MAY_BEGIN (README created; 2 blockers: no live env + missing frontend requirements.txt)

---

## 1. Feature 3.6 Gate

Feature 3.6: FAIL — NOT_CLOSED (F36-B01: no live Python env).
Feature 3.7 gate: **DOCUMENTATION_MAY_BEGIN_WITH_UPSTREAM_WARNINGS**.
Rules: may use F3.6 scripts/architecture facts as-is; may NOT cite unverified F3.6 benchmark numbers.

## 2. Repository Inventory

26 items classified across: BACKEND, FRONTEND, MODEL_ARTIFACT, DATA, SCRIPT, DEMO_ASSET, TEST, DOC, REPORT, CONFIG, OTHER.

Canonical structure:
- Backend: `5.UNG_DUNG/5.1.backend_api/`
- Frontend: `epic3/feature_3_3/frontend/`
- Artifacts: `artifacts/epic2/`
- Scripts: `scripts/`

## 3. Repository Structure Decision

**Decision: DOCUMENT_ONLY.** Split structure (5.UNG_DUNG vs epic3/) is historical artifact of project evolution — both are live and functional. Moving files would break hardcoded artifact paths and cross-feature imports. Do NOT move files.

## 4. Dependency Sources

| Source | Canonical | Purpose |
|---|---|---|
| 5.UNG_DUNG/5.1.backend_api/requirements.txt | ✅ | Backend FastAPI runtime |
| 7.ML/7.10.model_packaging/package/requirements-*.txt | ❌ | Historical; superseded |
| 5.UNG_DUNG/5.3.config/requirements.txt | ❌ | Database config (psycopg2-binary); not API runtime |
| frontend requirements.txt | ❌ | **MISSING** — streamlit + httpx imported but no spec |

**Frontend requirements.txt:** Created `epic3/feature_3_3/frontend/requirements.txt` (hotfix Phase 1) with streamlit>=1.30.0 and httpx>=0.27.0. F37-B02 resolved.

## 5. Import Matrix

14 packages reviewed. Backend dependencies verified from actual Python imports: fastapi, uvicorn, pydantic, numpy, pandas, joblib, scikit-learn, xgboost, shap. Frontend: streamlit (runtime, MISSING from any requirements.txt), httpx (runtime, MISSING). pytest in test files but no requirements-dev.txt.

## 6. README.md

Created at `README.md` (canonical project root). Contains: overview, key features table, ASCII architecture diagram, tech stack, quick start with exact commands, repository structure tree, documentation links table, testing summary, model overview, limitations summary, demo reliability links.

**Verified facts:** project name, model type/ID/version, feature counts, dataset rows, endpoint list, page list, architecture (0 direct model loads in frontend), limitation language.

**Python version:** 3.13.7 — VERIFIED from source `9.SCRIPTS/feature_2_2_preprocessing.py` line 43.

## 7. Broken Links

4 intentional placeholders (docs not yet created):
- `HOW_TO_RUN_APP.md` → Phase 2
- `USER_MANUAL.md` → Phase 3
- `API_DOCUMENTATION.md` → Phase 3
- `TECHNICAL_APPENDIX.md` → Phase 4

All other file references (scripts, requirements, artifacts) point to existing files.

## 8. Command Validation

6 commands in README Quick Start. **0 tested live** (no Python env). Commands are structurally correct based on source review of scripts/.

## 9. Claim Audit

11 claims checked. **0 unsupported.** Python 3.13.7 VERIFIED from source `9.SCRIPTS/feature_2_2_preprocessing.py` line 43.

**Accuracy/production/causal/production claims: 0** — no fabricated quality claims.

## 10. Gate

```
status:  FAIL
warnings: 2 (F37-W01 broken links, F37-W02 commands untested) [F37-W03 resolved]
blockers: 1 (F37-B01 live env)  [F37-B02 resolved by creating epic3/feature_3_3/frontend/requirements.txt — hotfix Phase 1]
next:     MAY_BEGIN
```
