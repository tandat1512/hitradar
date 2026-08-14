# How to Run HitRadar Pro

This guide covers local setup and startup for the current FastAPI + static frontend app.

## Project Layout

```text
HitRadar_Pro/
- 5.UNG_DUNG/5.1.backend_api/   FastAPI backend
- 5.UNG_DUNG/5.2.frontend/      static HTML/CSS/JS frontend
- artifacts/epic2/              model packaging artifacts
- scripts/                      startup scripts
- 5.DATA/processed/             training dataset
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r 5.UNG_DUNG/5.3.config/requirements.txt
```

The frontend is plain HTML/CSS/JS and does not require npm or Streamlit.

## Environment

| Variable | Default | Description |
|---|---:|---|
| `BACKEND_BASE_URL` | `http://localhost:8000` | Backend API base URL |
| `BACKEND_PORT` | `8000` | Backend bind port |
| `BACKEND_HOST` | `127.0.0.1` | Backend bind address |
| `BACKEND_HEALTH_TIMEOUT` | `120` | Seconds to wait for backend readiness |
| `FRONTEND_PORT` | `8501` | Frontend port |
| `STREAMLIT_SERVER_PORT` | `8501` | Legacy fallback for frontend port |
| `HITRADAR_CORS_ORIGINS` | `http://127.0.0.1:8501,http://localhost:8501` | Allowed browser origins |

If `BACKEND_PORT` is changed, update the Backend URL field in the UI or open the frontend with `?api=http://localhost:<port>`.

## Required Artifacts

Before starting, confirm model artifacts are present:

```text
artifacts/epic2/pipeline/full_inference_pipeline.joblib
artifacts/epic2/schemas/input_schema.json
```

The running backend also uses the canonical model artifacts under `4.MODELS/`.

## Start The App

Full stack:

```bash
python scripts/run_all.py
```

Separate terminals:

```bash
python scripts/run_backend.py
python scripts/run_frontend.py
```

URLs:

| Service | URL |
|---|---|
| Frontend UI | http://localhost:8501 |
| Backend API | http://127.0.0.1:8000 |
| Backend docs | http://127.0.0.1:8000/docs |

## Demo Flow

```text
Predict -> Cluster -> Similar -> Insights
```

The frontend remains inspectable if the backend is offline, but live prediction, clustering, and recommendation require FastAPI.

## Troubleshooting

Dependency error:

```bash
pip install -r 5.UNG_DUNG/5.3.config/requirements.txt
```

Port already in use:

```bash
set BACKEND_PORT=8002
set FRONTEND_PORT=8502
python scripts/run_all.py
```

Backend unavailable:

```bash
python scripts/run_backend.py
```

Wait until it reports `Backend healthy`, then start the frontend.

Frontend unavailable:

```bash
set FRONTEND_PORT=8502
python scripts/run_frontend.py
```

## Stop

Press Ctrl+C in the launcher terminal. The scripts only stop processes they started.
