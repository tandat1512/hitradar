# HITRADAR PRO — DEMO RELIABILITY CHECKLIST

Feature 3.6.12 · Người thực hiện: Minh · Ngày: 2026-08-07

> Dùng checklist này trước và trong buổi demo. Mọi mục live phải được xác nhận
> trong environment thật (không có Python env trong phiên chuẩn bị này — xem
> runbook để unblock).

## 1. Before Demo Day

- [ ] Tested commit/source snapshot identified
- [ ] Python version verified
- [ ] Dependencies installed
- [ ] Required artifacts available (`artifacts/epic2/`)
- [ ] Backup screenshots available
- [ ] Backup video status verified
- [ ] Offline demo package verified

## 2. Environment

- [ ] Backend environment variables configured
- [ ] Frontend API URL configured
- [ ] Artifact root valid
- [ ] No secrets missing for local demo
- [ ] Backend port available
- [ ] Frontend port available

## 3. Backend Check

- [ ] run_backend works (`python scripts/run_backend.py`)
- [ ] /health returns expected status
- [ ] model_ready = true
- [ ] model version correct (1.0.0)
- [ ] canonical Predict succeeds (46.421062 ± 0.001)

## 4. Frontend Check

- [ ] run_frontend works (`python scripts/run_frontend.py`)
- [ ] Home opens
- [ ] backend status Connected
- [ ] navigation works

## 5. Core Demo

- [ ] Predict
- [ ] Explain
- [ ] What-if
- [ ] Music Trends
- [ ] Model Info
- [ ] Responsible Use

## 6. run_all

- [ ] run_all starts backend
- [ ] waits for /health
- [ ] starts frontend
- [ ] prints URLs
- [ ] Ctrl+C cleanup works

## 7. Failure Backup

- [ ] Backend-unavailable state works
- [ ] Offline mode clearly labeled
- [ ] Prepared Predict works
- [ ] Prepared Explain works
- [ ] Prepared What-if works
- [ ] Live recovery works

> Lưu ý thật: offline Explain và What-if hiện NOT_AVAILABLE (không có SHAP/delta
> đã validate). Khi demo offline, chỉ Predict (canonical) + Model Info + Trends
> khả dụng. Không bịa kết quả.

## 8. Media Backup

- [ ] Home screenshot
- [ ] Predict screenshot
- [ ] Explain screenshot
- [ ] What-if screenshot
- [ ] Trends screenshot
- [ ] Model Info screenshot
- [ ] Responsible Use screenshot
- [ ] Video status checked

## 9. Five Minutes Before Demo

- [ ] Power/charger ready
- [ ] Correct source snapshot
- [ ] Ports free
- [ ] run_all smoke successful
- [ ] Canonical demo input available
- [ ] Offline fallback ready
- [ ] Backup media locally accessible
