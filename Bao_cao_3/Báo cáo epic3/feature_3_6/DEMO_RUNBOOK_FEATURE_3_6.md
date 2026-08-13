# HitRadar Pro Demo Runbook

Feature 3.6.13 · Người thực hiện: Minh · Ngày: 2026-08-07

---

## 1. Tested Environment

| Item | Value |
|---|---|
| Python | CAPTURE_LIVE (yêu cầu ≥3.10; chưa có live env để xác nhận) |
| OS | Windows 11 Home Single Language 10.0.26200 |
| Tested commit | WORKING_TREE 2026-08-07 (xác nhận lại `git rev-parse HEAD` trước demo) |
| Model version | 1.0.0 (EXP24-XGB-FINAL-001) |

## 2. Ports

| Component | Host | Port | Đặt qua |
|---|---|---|---|
| Backend (FastAPI/uvicorn) | 127.0.0.1 | 8000 | `BACKEND_PORT` (scripts) / `PORT` (.env.example) |
| Frontend (Streamlit) | 127.0.0.1 | 8501 | `STREAMLIT_SERVER_PORT` (scripts) |

Nếu port bị chiếm: **không kill process lạ** — đổi port bằng env var và trỏ `BACKEND_BASE_URL` cho khớp (xem §12).

## 3. Required Environment Variables

| Variable | Component | Required | Example | Purpose |
|---|---|---|---|---|
| `ARTIFACTS_PATH` | backend | No (default `artifacts/epic2`) | `artifacts/epic2` | Artifact root (pipeline/schemas/metadata) |
| `BACKEND_PORT` | run scripts | No (default 8000) | `8000` | Backend bind port |
| `BACKEND_HOST` | run scripts | No (default 127.0.0.1) | `127.0.0.1` | Backend bind host |
| `BACKEND_HEALTH_TIMEOUT` | run scripts | No (default 120) | `120` | Seconds to wait for /health |
| `STREAMLIT_SERVER_PORT` | run scripts | No (default 8501) | `8501` | Frontend port |
| `BACKEND_BASE_URL` | frontend | No (default `http://localhost:8000`) | `http://localhost:8000` | Frontend → backend URL; set explicitly when overriding `BACKEND_PORT` in `run_all.py` |
| `BACKEND_CONNECT_TIMEOUT` | frontend | No (default 5.0) | `5.0` | httpx connect timeout |
| `BACKEND_READ_TIMEOUT` | frontend | No (default 30.0) | `30.0` | httpx read timeout |
| `BACKEND_REQUEST_TIMEOUT` | frontend | No (default 35.0) | `35.0` | httpx total timeout |
| `API_PREFIX` | backend+frontend | No (default empty) | `` | Optional route prefix |
| `MODEL_LOAD_STRATEGY` | backend (.env) | No (default eager) | `eager` | Eager model load at startup |
| `CORS_ALLOWED_ORIGINS` | backend (.env) | No | `http://localhost:8501,...` | CORS origins |
| `OFFLINE_DEMO_MODE` | frontend (offline) | No | `true` | Explicit offline demo activation |

Không ghi giá trị secret ở đây. `.env.example` canonical: `epic3/feature_3_2/backend/.env.example`.

## 4. Important Paths / Configuration

- Backend entrypoint: `5.UNG_DUNG/5.1.backend_api/api.py` (module `api:app`)
- Backend config: `5.UNG_DUNG/5.1.backend_api/config.py`
- Frontend entrypoint: `epic3/feature_3_3/frontend/app.py`
- Frontend config: `epic3/feature_3_3/frontend/core/config.py`
- Model: `artifacts/epic2/pipeline/full_inference_pipeline.joblib`
- Schemas: `artifacts/epic2/schemas/` · Metadata: `artifacts/epic2/metadata/`
- Canonical example: `artifacts/epic2/examples/example_input.json`
- Offline evidence: `demo/offline/evidence/`
- Backup screenshots: `demo/backup/screenshots/`
- Backup video: `demo/backup/video/hitradar_demo.mp4`

## 5. Start Backend

```
python scripts/run_backend.py
```

- Expected console: `[CHECK] ... artifact root ...` → `[START] python -m uvicorn api:app ...` → `[READY] Backend healthy: http://127.0.0.1:8000 (model_loaded=true)`
- Health URL: `GET http://127.0.0.1:8000/health`
- Ready condition: HTTP 200 **và** `model_loaded == true`

## 6. Start Frontend

```
python scripts/run_frontend.py
```

- URL: `http://localhost:8501`
- Backend unreachable → WARN (frontend vẫn mở; các page dùng API sẽ báo lỗi đến khi backend lên).

## 7. Start Everything

```
python scripts/run_all.py
```

- Flow: validate config → start backend → **poll real /health (không fixed sleep)** → start frontend → in URL → monitor → Ctrl+C cleanup (chỉ kill process mình tạo).
- In ra:
  - Backend API: `http://127.0.0.1:8000`
  - Frontend UI: `http://localhost:8501`

## 8. Normal Demo Flow

1. Home
2. Predict Popularity (canonical input → 46)
3. SHAP Explanation
4. What-If Simulator
5. Music Trends
6. Model Info
7. Limitations & Responsible Use

## 9. Backend Does Not Start

Check:
- Python + dependencies (requirements: fastapi, uvicorn, xgboost, shap, joblib, ...)
- Entrypoint tồn tại (`5.UNG_DUNG/5.1.backend_api/api.py`)
- Artifact root đúng (`ARTIFACTS_PATH` / `artifacts/epic2`)
- Port 8000 trống
- Log lỗi từ uvicorn (script để console)

## 10. /health Not Ready

Check:
- Model/artifacts đầy đủ (script validate trước khi start)
- `ARTIFACTS_PATH` khớp hash/config
- Log backend

**KHÔNG retrain model.** Nếu model hỏng → dùng offline mode + backup media.

## 11. Frontend Cannot Connect

Check:
- Backend đang chạy?
- `BACKEND_BASE_URL` đúng port?
- CORS: `CORS_ALLOWED_ORIGINS` chứa `http://localhost:8501`
- `GET /health` từ trình duyệt

## 12. Port Already in Use

Xác định: `netstat -ano | findstr :8000` (hoặc script in "port already in use" + exit 2).
Không kill process lạ. Đổi port:

```
set BACKEND_PORT=8001
set BACKEND_BASE_URL=http://localhost:8001
python scripts/run_all.py
```

## 13. Live Predict Fails

- Retry 1 lần (thoáng timeout).
- Ghi `request_id` + xem log backend.
- Quyết định fallback: offline mode (§14) hoặc backup media.

## 14. Offline Demo Mode

Activation (explicit):
```
set OFFLINE_DEMO_MODE=true
python scripts/run_frontend.py
```
hoặc khi API down, UI offer "Switch to Offline Demo Mode".

Supports:
- Predict với **canonical prepared scenario** (46, precomputed validated evidence)
- Model Info (validated snapshot, labeled version + time)
- Music Trends (tính từ dataset local — labeled local, không phải API snapshot)

**KHÔNG supports:** Explain (no validated SHAP), What-If (no validated delta) — không bịa.

Disclaimer bắt buộc trên mọi page:
> OFFLINE DEMO MODE — Precomputed validated result. No live model inference is being performed.

## 15. Screenshots

- Directory: `demo/backup/screenshots/`
- Manifest: `feature_3_6/validation/feature_3_6_backup_screenshot_manifest.json`
- 7 ảnh chuẩn (Home, Predict, Explain, What-If, Trends, Model Info, Responsible Use). **Chưa capture** (cần live env).

## 16. Backup Video

- Path: `demo/backup/video/hitradar_demo.mp4`
- Status: **MANUAL_RECORDING_REQUIRED** (shot list: `feature_3_6/validation/feature_3_6_demo_video_shot_list.md`).

## 17. Return to Live Mode

1. Khôi phục API (start backend).
2. Frontend: Retry / "Switch back to Live" → `demo_mode = LIVE`.
3. Xác nhận banner offline biến mất, `GET /health` OK.

## 18. Graceful Shutdown

- `run_all`: Ctrl+C → dừng frontend rồi backend (chỉ process mình tạo), exit 0.
- `run_backend` / `run_frontend`: Ctrl+C → dừng sạch.
- Không để orphan; không kill process lạ.
