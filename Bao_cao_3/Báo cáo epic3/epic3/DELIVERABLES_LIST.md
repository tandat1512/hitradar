# DELIVERABLES LIST — EPIC 3: Productization, Integration & Defense
**Ngày lập:** 2026-07-30
**Người phụ trách:** Minh
**Nguồn tham chiếu:** Chi tiết EPIC 3 và hiểu nhiệm vụ các feature (1).docx

> Mỗi mục bên dưới là một sản phẩm phải có khi EPIC 3 hoàn thành. Checklist này dùng để nghiệm thu và đảm bảo không bỏ sót deliverables.

---

## Nhóm 1: Backend (FastAPI)

- `[ ]` FastAPI app chạy ổn định
- `[ ]` Endpoint `GET /health` — trả về trạng thái service
- `[ ]` Endpoint `GET /model-info` — trả về model_id, model_version, package_version, data_version, metrics
- `[ ]` Endpoint `GET /features` — trả về danh sách 18 input features + selected features
- `[ ]` Endpoint `POST /predict` — nhận input body (18 fields), trả về prediction_raw, prediction_clipped, prediction_display, warnings
- `[ ]` Endpoint `POST /explain` — nhận input, trả về SHAP values, base_value, top contributions cho từng feature
- `[ ]` Endpoint `POST /what-if` — nhận original input + modified input, trả về so sánh 2 predictions
- `[ ]` Pydantic request/response schemas cho tất cả endpoints
- `[ ]` CORS middleware enable
- `[ ]` Centralized error handling + logging
- `[ ]` Config quản lý artifact paths (không hardcode)
- `[ ]` `.env.example` với PORT, ARTIFACT_PATH
- `[ ]` Unit tests cho /health, /predict, /explain, /what-if
- `[ ]` OpenAPI schema export (auto từ FastAPI)

---

## Nhóm 2: Frontend (Streamlit)

- `[ ]` Streamlit multi-page app chạy ổn định
- `[ ]` Trang **Home / Project Overview** — giới thiệu dự án HitRadar Pro
- `[ ]` Trang **Predict Popularity** — form nhập 18 features, gọi `/predict`, hiển thị kết quả (raw, clipped, display)
- `[ ]` Trang **SHAP Explanation** — hiển thị SHAP summary bar chart, beeswarm, top feature contributions cho prediction vừa chạy
- `[ ]` Trang **What-If Simulator** — slider/input cho phép thay đổi từng feature, gọi `/what-if`, hiển thị so sánh 2 predictions
- `[ ]` Trang **Music Trends 1921–2020** — biểu đồ popularity trend, audio features trend, explicit trend, duration trend theo decade
- `[ ]` Trang **Model Info** — hiển thị model version, data version, metrics (MAE, RMSE, R2), residual distribution
- `[ ]` Trang **Limitations & Responsible Use** — giới hạn model, khuyến cáo sử dụng, data biases
- `[ ]` API client module gọi FastAPI (base URL configurable)
- `[ ]` Layout/sidebar/navigation thống nhất
- `[ ]` Component prediction result (loading, error, success states)
- `[ ]` Component SHAP explanation (chart + text)
- `[ ]` Component what-if comparison (diff view)
- `[ ]` Component error/warning/loading states
- `[ ]` Smoke test navigation giữa các trang

---

## Nhóm 3: Scripts

- `[ ]` Script `run_backend.py` hoặc `run_backend.bat` — khởi động FastAPI (uvicorn)
- `[ ]` Script `run_frontend.py` hoặc `run_frontend.bat` — khởi động Streamlit
- `[ ]` Script `run_all.py` hoặc `run_all.bat` — khởi động cả backend và frontend cùng lúc

---

## Nhóm 4: Tài liệu

- `[ ]` `README.md` — giới thiệu dự án, cấu trúc repo, cách cài đặt nhanh
- `[ ]` `requirements.txt` hoặc `environment.yml` — tổng hợp tất cả dependencies (FastAPI + Streamlit + ML + SHAP)
- `[ ]` `HOW_TO_RUN_APP.md` — hướng dẫn cài đặt từ đầu, chạy backend, chạy frontend, chạy run_all
- `[ ]` `USER_MANUAL.md` — hướng dẫn sử dụng cho người dùng cuối (không cần biết code)
- `[ ]` `API_DOCUMENTATION.md` — mô tả chi tiết từng endpoint, request/response format, ví dụ
- `[ ]` `TECHNICAL_APPENDIX.md` — chi tiết kỹ thuật: cấu trúc artifact, schema, SHAP assets, pipeline flow
- `[ ]` Báo cáo tổng hợp dự án (tích hợp EPIC 1 + EPIC 2 + EPIC 3)

---

## Nhóm 5: Test & Reliability

- `[ ]` `docs/epic3/artifact_validation_report.md` — báo cáo Feature 3.1: kết quả validate từng artifact, latency benchmark, load test
- `[ ]` `docs/epic3/e2e_test_report.md` — báo cáo Feature 3.5: kết quả test từng luồng E2E, bugs đã fix
- `[ ]` `docs/epic3/demo_reliability_checklist.md` — báo cáo Feature 3.6: port config, env vars, fallback khi lỗi, backup mode

---

## Nhóm 6: Backup Demo

- `[ ]` Screenshots của tất cả các trang Streamlit (mỗi trang ≥ 1 screenshot)
- `[ ]` Video demo ngắn (1–3 phút) chạy toàn bộ luồng: Predict → Explain → What-If
- `[ ]` Offline demo mode — nếu API không chạy, frontend vẫn hiển thị được screenshots/video mẫu

---

## Nhóm 7: Bảo vệ

- `[ ]` Slide bảo vệ (PowerPoint hoặc tương đương)
- `[ ]` Demo script — kịch bản demo chi tiết từng bước cho người thuyết trình
- `[ ]` Câu chuyện dự án — narrative tổng hợp EPIC 1 → EPIC 2 → EPIC 3
- `[ ]` Q&A về dataset — câu hỏi và câu trả lời về nguồn dữ liệu, chất lượng, giới hạn
- `[ ]` Q&A về model — câu hỏi và câu trả lời về thuật toán, hyperparameter, metrics
- `[ ]` Q&A về SHAP — câu hỏi và câu trả lời về explainability
- `[ ]` Q&A về giới hạn dự án — câu hỏi và câu trả lời về những gì dự án không làm được
- `[ ]` Phân công người thuyết trình cụ thể
- `[ ]` Rehearse demo lần 1 — ghi nhận phản hồi
- `[ ]` Rehearse demo lần 2 — chạy thử cuối trước bảo vệ
- `[ ]` Final defense checklist — kiểm tra tất cả artifacts, báo cáo, slide đã sẵn sàng

---

## Nhóm 8: Final Delivery

- `[ ]` Tất cả code đã commit lên GitHub / final commit
- `[ ]` Release tag (nếu có)
- `[ ]` Kiểm tra tất cả artifacts nằm đúng thư mục
- `[ ]` Báo cáo + slide đã nộp
- `[ ]` Demo thực tế cho giảng viên/thầy
- `[ ]` Bảo vệ thành công
- `[ ]` Retrospective EPIC 3 — ghi nhận bài học

---

## Tổng kết

| Nhóm | Số mục | Đã hoàn thành | Còn lại |
|------|--------|--------------|--------|
| 1. Backend | 15 | 0 | 15 |
| 2. Frontend | 18 | 0 | 18 |
| 3. Scripts | 3 | 0 | 3 |
| 4. Tài liệu | 7 | 0 | 7 |
| 5. Test & Reliability | 3 | 0 | 3 |
| 6. Backup Demo | 3 | 0 | 3 |
| 7. Bảo vệ | 11 | 0 | 11 |
| 8. Final Delivery | 8 | 0 | 8 |
| **Tổng** | **68** | **0** | **68** |
