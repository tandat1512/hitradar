# How to Run HitRadar Pro

This guide covers setup, configuration, and startup from a clean environment.

**Prerequisites:** Python 3.13.14 in the validated defense environment (minimum ≥3.10)

---

## 1. Get the Project

Download or copy the repository to a local directory. No private URLs required.

```
HitRadar_Pro/
├── 5.UNG_DUNG/5.1.backend_api/     ← FastAPI backend
├── epic3/feature_3_3/frontend/      ← Streamlit frontend
├── artifacts/epic2/                  ← Model artifacts
├── scripts/                          ← Startup scripts
└── 5.DATA/processed/               ← Training dataset
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows activate
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

---

## 3. Install Dependencies

**Backend:**
```bash
pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt
```

**Frontend:**
```bash
pip install -r epic3/feature_3_3/frontend/requirements.txt
```

**Both (combined):**
```bash
pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt \
               -r epic3/feature_3_3/frontend/requirements.txt
```

Installed packages include: fastapi, uvicorn, pydantic, numpy, pandas, joblib, scikit-learn, xgboost, shap, streamlit, httpx.

---

## 4. Configure Environment

No `.env` file is required for a local demo run. Default values work out of the box:

| Variable | Default | Description |
|---|---|---|
| `BACKEND_BASE_URL` | `http://localhost:8000` | Backend API base URL |
| `BACKEND_PORT` | `8000` | Backend bind port |
| `BACKEND_HOST` | `127.0.0.1` | Backend bind address |
| `BACKEND_HEALTH_TIMEOUT` | `120` | Seconds to wait for backend readiness |
| `STREAMLIT_SERVER_PORT` | `8501` | Frontend port |
| `ARTIFACTS_PATH` | `<repo>/artifacts/epic2` | Model artifact root |

Override with environment variables if needed (e.g., to avoid port conflicts). If `BACKEND_PORT` is changed, set `BACKEND_BASE_URL=http://localhost:<same-port>` explicitly in the parent shell before running `scripts/run_all.py`; the current launcher does not reliably propagate a derived URL to the frontend child process.

---

## 5. Verify Required Artifacts

Before starting, confirm model artifacts are present:

```
artifacts/epic2/pipeline/full_inference_pipeline.joblib
artifacts/epic2/schemas/input_schema.json
```

If missing: run Feature 3.1 packaging first, or set `ARTIFACTS_PATH` to the correct `artifacts/epic2` root.

**Do not retrain or regenerate model artifacts.** These are read-only inputs to the FastAPI backend.

---

## 6. Start the Application

### Option A — Full Stack (Recommended)

```bash
python scripts/run_all.py
```

This script:
1. Validates artifact presence
2. Starts the backend
3. Polls `GET /health` until `model_loaded == true`
4. Starts the frontend
5. Prints both URLs
6. Monitors both processes
7. Stops both on Ctrl+C (or if either crashes)

### Option B — Individual Terminals

**Terminal 1 — Backend:**
```bash
python scripts/run_backend.py
```

Backend starts on `http://127.0.0.1:8000`.
Waits for model load before reporting READY.
Stops on Ctrl+C.

**Terminal 2 — Frontend:**
```bash
python scripts/run_frontend.py
```

Frontend starts on `http://localhost:8501`.
If backend is unreachable, shows a **WARN** message (does not exit) — API pages will show errors until backend is up.

---

## 7. Access the Application

| Service | URL |
|---|---|
| Frontend (Streamlit UI) | http://localhost:8501 |
| Backend API | http://127.0.0.1:8000 |
| Backend API docs | http://127.0.0.1:8000/docs |

---

## 8. Normal Demo Flow

```
Home → Predict Popularity → SHAP Explanation → What-If Simulator
     → Music Trends → Model Info → Limitations & Responsible Use
```

See [USER_MANUAL.md](USER_MANUAL.md) for detailed page instructions.

---

## 9. Stop the Application

**Ctrl+C** — sends interrupt signal; `run_all.py` (or `run_backend.py`/`run_frontend.py`) gracefully stops its own processes.

Do NOT manually kill Python processes unless the script hangs — the scripts only manage their own child processes, not unrelated ones.

---

## 10. Troubleshooting

### Dependency error on startup

```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:** Reinstall dependencies:
```bash
pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt
pip install -r epic3/feature_3_3/frontend/requirements.txt
```

---

### Backend won't start — artifact error

```
[ERROR] Required artifacts not found:
  - artifacts/epic2/pipeline/full_inference_pipeline.joblib
  - artifacts/epic2/schemas/input_schema.json
```

**Fix:** Verify `artifacts/epic2/` directory exists and is populated. Or set `ARTIFACTS_PATH` to the correct artifact root.

---

### Port already in use

```
[ERROR] backend port 8000 on 127.0.0.1 is already in use.
```

**Fix:** Stop the existing service on that port, or override with an environment variable:

```bash
set BACKEND_PORT=8002
python scripts/run_backend.py
```

For the frontend: `set STREAMLIT_SERVER_PORT=8502`

---

### Backend unavailable — frontend can't connect

Frontend shows red "Backend Unavailable" in sidebar.

**Fix:** Start the backend first:
```bash
python scripts/run_backend.py
```
Wait until it reports `Backend healthy: http://127.0.0.1:8000 (model_loaded=true)`, then start the frontend.

---

### Model not ready — health timeout

```
[ERROR] /health not ready within 120s at http://127.0.0.1:8000/health
```

**Fix:** Increase timeout with:
```bash
set BACKEND_HEALTH_TIMEOUT=300
python scripts/run_backend.py
```
Or verify the artifact files are not corrupted.

---

### Streamlit won't start

```
Streamlit server startup failed.
```

**Fix:** Check that port 8501 (or the configured `STREAMLIT_SERVER_PORT`) is free:
```bash
set STREAMLIT_SERVER_PORT=8502
python scripts/run_frontend.py
```

---

## 11. Offline Demo Fallback

If the backend cannot start and you need to demonstrate the UI:

The Offline Demo Mode provides precomputed validated demonstration pages. **This is not a live model — it is a static fallback for presentation purposes only.**

Activate via `OFFLINE_DEMO_MODE=true` or through the UI prompt when the backend is unreachable.

**On offline mode:**
- Predict page shows precomputed example(s)
- SHAP Explanation and What-If Simulator are **not available** offline
- Music Trends loads from local dataset (does not require backend)

See `Bao_cao_3/Báo cáo epic3/feature_3_6/validation/feature_3_6_offline_demo_mode_contract.json` for the full offline mode specification.

---

## 12. Port Reference

| Port | Service | Default |
|---|---|---|
| `8000` | FastAPI Backend | `BACKEND_PORT` env var |
| `8501` | Streamlit Frontend | `STREAMLIT_SERVER_PORT` env var |

Both ports must be free before starting. If either port is occupied, the script refuses to start and exits with code 2 — it does **not** kill existing processes.

---

## 13. Further Documentation

| Document | Description |
|---|---|
| [README.md](README.md) | Project overview, architecture, tech stack |
| [USER_MANUAL.md](USER_MANUAL.md) | End-user guide for all pages |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API endpoint reference |
| [TECHNICAL_APPENDIX.md](TECHNICAL_APPENDIX.md) | Model details, data schema |
| [Bao_cao_3/Báo cáo epic3/feature_3_6/DEMO_RUNBOOK_FEATURE_3_6.md](Bao_cao_3/Báo%20cáo%20epic3/feature_3_6/DEMO_RUNBOOK_FEATURE_3_6.md) | Demo day runbook |
