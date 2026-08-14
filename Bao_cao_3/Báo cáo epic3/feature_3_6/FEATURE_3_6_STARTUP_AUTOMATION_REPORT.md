# Feature 3.6 — Startup Automation Report
## Phase 3 — run_backend / run_frontend / run_all

**Feature:** 3.6 — Performance, Reliability & Demo Backup
**Phase:** 3 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (no live Python env; scripts created & structurally validated)

---

## 1. Delivered Scripts

| Script | Purpose | Command |
|---|---|---|
| [scripts/run_backend.py](../../scripts/run_backend.py) | Start FastAPI backend | `python scripts/run_backend.py` |
| [scripts/run_frontend.py](../../scripts/run_frontend.py) | Start Streamlit frontend | `python scripts/run_frontend.py` |
| [scripts/run_all.py](../../scripts/run_all.py) | Full demo stack | `python scripts/run_all.py` |
| [scripts/_common.py](../../scripts/_common.py) | Shared stdlib helpers | imported |

**Supported platform:** Windows (primary). Scripts are pure Python + stdlib → also POSIX-compatible.

**Canonical commands confirmed from source:**

```
# Backend  (cwd 5.UNG_DUNG/5.1.backend_api)
python -m uvicorn api:app --host 127.0.0.1 --port 8000
# health: GET /health → {status: healthy, model_loaded: true}

# Frontend (cwd epic3/feature_3_3/frontend)
python -m streamlit run app.py --server.port 8501
# health: GET /_stcore/health → 200 "ok"
```

---

## 2. run_backend.py Behavior

1. Resolves repo root from `__file__` (no machine paths).
2. Validates artifact root: `artifacts/epic2/pipeline/full_inference_pipeline.joblib` + `schemas/input_schema.json` exist (or `ARTIFACTS_PATH`).
3. Port conflict: **refuses to start, prints `[ERROR] ... port 8000 on 127.0.0.1 is already in use` + override hint, exits 2 — never kills.**
4. Starts exact uvicorn command; sets `ARTIFACTS_PATH`.
5. Polls `/health` until `model_loaded == true` (no fixed sleep).
6. **Technical note:** Because the backend uses **eager load in `lifespan`**, the HTTP endpoint at port 8000 is only reachable AFTER the model has been fully deserialized. Consequently, `model_loaded` is **always true** by the time the first HTTP 200 response is returned. The poll therefore has two effects: (a) it waits for uvicorn to finish startup and bind the port, and (b) it verifies the endpoint is responding before reporting READY. The intermediate `model_loaded=false` state is never observable over HTTP.
6. Backend dies before ready → reports exit code, exits 3.
7. Ctrl+C → graceful stop of the backend it started.
8. Propagates backend exit code.

Env overrides: `BACKEND_HOST`, `BACKEND_PORT`, `ARTIFACTS_PATH`, `BACKEND_HEALTH_TIMEOUT`.

---

## 3. run_frontend.py Behavior

1. Resolves `app.py` entrypoint.
2. Port conflict on 8501 → refuses, exits 2.
3. Probes backend `/health`; unreachable → **WARN (not fail)** — offline mode may be added later; API pages will show errors until backend up.
4. Starts `streamlit run app.py --server.port X --server.headless true`; sets `BACKEND_BASE_URL`.
5. Waits for `/_stcore/health` ready; Ctrl+C cleanup; propagates exit code.

Env overrides: `STREAMLIT_SERVER_PORT`, `BACKEND_BASE_URL`, `BACKEND_HEALTH_TIMEOUT`.

---

## 4. run_all.py Flow

```
validate config (entrypoints, artifacts)
      ↓
start backend process
      ↓
poll GET /health → model_loaded == true      ← real readiness, NO fixed sleep
      ↓
READY?  NO  → stop backend, exit 3
        YES → start frontend process
      ↓
Note on eager-load health: since FastAPI binds the HTTP port only after lifespan
(startup) completes, the first reachable /health is always model_loaded=true.
The poll is still correct: it waits for the port to be listening AND verifies the
endpoint is responding. No race condition exists in practice.
      ↓
poll /_stcore/health
      ↓
frontend exited? → stop backend (no orphan), exit 3
      ↓
print URLs:  Backend API: http://127.0.0.1:8000
             Frontend UI: http://localhost:8501
      ↓
monitor both children
      ↓
Ctrl+C / child failure → teardown: frontend first, then backend (own children only)
```

- Backend fails before health → detected via `child.poll()` (no hang on full timeout).
- Port occupied → exit 2, nothing killed.
- Teardown always in `finally` → no launcher-created orphans.

---

## 5. Port Handling (both scripts)

- Occupied port → **print + exit 2**, never kill.
- `is_port_in_use()` is a plain TCP connect probe — harmless, no side effects.
- Env overrides allow tests to use non-default ports without touching dev services.

---

## 6. Health Readiness

- Backend: `GET /health`, ready **only** when HTTP 200 **and** `model_loaded == true`.
- Frontend: `GET /_stcore/health` (plain "ok") → ready.
- No `sleep(3)` anywhere.

**Technical note on eager-load health:** Because FastAPI binds the HTTP port only after
`lifespan` completes, the model is already fully loaded (eager) before the first HTTP
200 can be returned. The intermediate `model_loaded=false` state is **never observable
over HTTP**. The poll correctly waits for the port to be listening AND verifies the
endpoint is responding — no race condition exists in this architecture.

---

## 7. Process Ownership & Shutdown

- PIDs tracked via `subprocess.Popen`.
- `terminate_child()`: graceful `CTRL_BREAK_EVENT` (Windows) / `SIGINT` (POSIX) → 5s grace → `terminate()` → `kill()` — **own children only**.
- Ctrl+C path verified by design in all 3 scripts (KeyboardInterrupt → finally teardown).

---

## 8. Env Contract

Scripts consume canonical names (no duplication):
`BACKEND_HOST`, `BACKEND_PORT`, `BACKEND_HEALTH_TIMEOUT`, `ARTIFACTS_PATH`, `STREAMLIT_SERVER_PORT`, `BACKEND_BASE_URL`, `BACKEND_*_TIMEOUT`, `API_PREFIX`. **Secrets in scripts: 0.**

---

## 9. Portability

- 0 machine-specific paths (`H:\`, `C:\Users\`, machine venv).
- Interpreter via `sys.executable` (no hardcoded venv activation).
- Dependency install is a setup concern, not a script runtime responsibility.
- Documented invocation: `python scripts/run_all.py` or `.venv\Scripts\python scripts/run_all.py`.

---

## 10. Validation Status

| Check | Design | Live |
|---|---|---|
| run_backend created + port handling | ✅ | ❌ BLOCKED |
| run_backend starts actual FastAPI | — | ❌ BLOCKED |
| run_frontend created + port handling | ✅ | ❌ BLOCKED |
| run_frontend starts actual Streamlit | — | ❌ BLOCKED |
| run_all created + health wait (no fixed sleep) | ✅ | ❌ BLOCKED |
| Backend/frontend failure handling | ✅ | ❌ BLOCKED |
| Process ownership / no foreign kills | ✅ | ❌ BLOCKED |
| Ctrl+C graceful shutdown | ✅ (design) | ❌ BLOCKED |
| Orphan processes after teardown | 0 (by design) | ❌ BLOCKED |
| Machine-specific paths | 0 | ✅ audited |
| Portability smoke (copy-repo) | — | ❌ BLOCKED |

---

## 11. Actual Commands (for the demo runner)

```bat
REM One command for the full demo:
python scripts\run_all.py

REM Individual:
python scripts\run_backend.py      REM terminal 1
python scripts\run_frontend.py     REM terminal 2
```

---

## 12. Warnings / Blockers

**Warnings:**
- F36-W07: Live startup validation blocked (scripts reviewed manually, not live-executed)
- F36-W08: Existing run.bat kept for backward compat; scripts/ is canonical
- F36-W11: Health readiness poll (`model_loaded=true`) is architecturally always true on first HTTP 200 due to eager lifespan load — documented in §4/§6

**Blockers:** F36-B01 (no live Python environment).

**Gate: FAIL — BLOCKED**
