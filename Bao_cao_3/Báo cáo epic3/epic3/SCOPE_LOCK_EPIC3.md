# SCOPE LOCK — EPIC 3: Productization, Integration & Defense
**Ngày chốt scope:** 2026-07-30
**Người phụ trách phiên này:** Minh
**Nguồn tham chiếu:** Chi tiết EPIC 3 và hiểu nhiệm vụ các feature (1).docx, Cập nhật Epic 3 (1).docx, HitRadar - Tổng hợp EPIC 1 2 3.docx

---

## EPIC 3 giải quyết vấn đề gì?

EPIC 3 biến các model artifacts đã được EPIC 2 huấn luyện và đóng gói thành một ứng dụng demo hoàn chỉnh có thể chạy trên máy tính cá nhân. Người dùng cuối (giảng viên, hội đồng bảo vệ, người xem demo) có thể nhập thông số bài hát, nhận dự đoán popularity, xem giải thích SHAP chi tiết, và chạy kịch bản what-if — mà không cần biết gì về code hay ML. Sản phẩm gồm FastAPI backend (cung cấp các API endpoint) và Streamlit frontend (giao diện đa trang thân thiện), kèm tài liệu đầy đủ và phương án demo dự phòng.

---

## EPIC 3 làm gì

| STT | Công việc | Mô tả |
|-----|-----------|--------|
| 1 | **Validate artifacts** | Kiểm tra toàn bộ artifacts từ EPIC 2 trước khi xây sản phẩm, đảm bảo model, schema, SHAP assets đều hợp lệ và load được. |
| 2 | **Xây FastAPI backend** | Backend REST API với các endpoint: `/health`, `/model-info`, `/features`, `/predict`, `/explain`, `/what-if`. Có service layer, Pydantic validation, error handling, logging, CORS. |
| 3 | **Xây Streamlit frontend** | App đa trang gồm: Home/Overview, Predict Popularity, SHAP Explanation, What-If Simulator, Music Trends 1921–2020, Model Info, Limitations & Responsible Use. |
| 4 | **Tích hợp E2E** | Kết nối Streamlit với FastAPI, test toàn bộ luồng predict/explain/what-if, test lỗi input/API. |
| 5 | **Benchmark & demo backup** | Đo latency API, tối ưu load model, cache artifacts, chuẩn bị screenshots/video/offline mode dự phòng nếu demo lỗi. |
| 6 | **Viết tài liệu** | README.md, HOW_TO_RUN_APP.md, USER_MANUAL.md, API_DOCUMENTATION.md, TECHNICAL_APPENDIX.md, báo cáo tổng hợp dự án. |
| 7 | **Chuẩn bị bảo vệ** | Slide bảo vệ, demo script, câu chuyện dự án, Q&A dataset/model/SHAP/giới hạn, phân công thuyết trình, rehearse. |
| 8 | **Final delivery** | Final commit, kiểm tra artifacts, nộp báo cáo + slide, demo, bảo vệ, retrospective. |

---

## EPIC 3 không làm gì

| STT | Không làm | Lý do |
|-----|-----------|--------|
| 1 | Không train model mới | Model đã được EPIC 2 huấn luyện và chọn best model. |
| 2 | Không clean data từ đầu | Dữ liệu đã được EPIC 1 clean và EPIC 2 dùng để train. |
| 3 | Không sửa feature engineering chính | Feature engineering đã được EPIC 2 chốt contract. |
| 4 | Không thay đổi model architecture | XGBoost champion bundle đã được EPIC 2 chọn và đóng gói. |
| 5 | Không biến EPIC 3 thành EPIC 2 lần hai | EPIC 3 chỉ packaging và demo, không làm lại ML. |

---

## Thứ tự thực thi khuyến nghị

1. Product Contract (3.0) → Artifact Validation Gate (3.1)
2. API Contract + Frontend Data Contract
3. FastAPI skeleton → Endpoint `/predict`
4. Streamlit gọi `/predict`
5. Endpoint `/explain` và `/what-if`
6. Streamlit Explain / What-if pages
7. Dashboard trends
8. E2E testing
9. Performance + backup demo
10. Documentation
11. Defense preparation
12. Final delivery

> **Nguyên tắc quan trọng:** Không bắt đầu bằng Streamlit. Luôn validate artifacts và FastAPI `/predict` trước.
