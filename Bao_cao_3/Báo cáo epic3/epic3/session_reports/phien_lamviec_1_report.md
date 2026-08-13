# BÁO CÁO NGHIỆM THU — PHIÊN 1: Task 3.0.1, 3.0.2, 3.0.3
**Người thực hiện:** Minh
**Ngày:** 2026-07-30
**Dự án:** HitRadar Pro — EPIC 3: Productization, Integration & Defense

---

## 1. Tóm tắt việc đã làm

### Task 3.0.1 — Chốt scope EPIC 3 ✅
Đã viết file `SCOPE_LOCK_EPIC3.md` tổng hợp toàn bộ phạm vi EPIC 3: 8 công việc chính (validate artifacts → FastAPI → Streamlit → E2E → benchmark → docs → bảo vệ → delivery), 5 điều cấm rõ ràng, và thứ tự thực thi khuyến nghị. Nguyên tắc quan trọng được ghi chú: không bắt đầu bằng Streamlit, luôn validate artifacts và `/predict` trước.

### Task 3.0.2 — Chốt input artifacts từ EPIC 2 ✅
Đã đọc trực tiếp `artifact_manifest.json`, `input_schema.json`, `output_schema.json`, và `MODEL_PACKAGE_README.md` từ repo. Danh sách đầy đủ 18 artifacts (Nhóm A: pipeline/schemas/metadata), 4 artifacts cần xác nhận (Nhóm B: metrics/residual/card/handoff), và ~12 SHAP assets (Nhóm C). Đề xuất cấu trúc thư mục chuẩn hoá `artifacts/epic2/` để EPIC 3 thống nhất artifact paths.

### Task 3.0.3 — Chốt output deliverables cuối cùng ✅
Đã viết file `DELIVERABLES_LIST.md` với 68 mục deliverables chia thành 8 nhóm: Backend (15), Frontend (18), Scripts (3), Tài liệu (7), Test & Reliability (3), Backup Demo (3), Bảo vệ (11), Final Delivery (8). Mỗi mục có checkbox `[ ]` để track tiến độ.

---

## 2. Danh sách file đã tạo

| STT | File | Mô tả |
|-----|------|--------|
| 1 | `docs/epic3/SCOPE_LOCK_EPIC3.md` | Task 3.0.1 — Chốt scope EPIC 3 |
| 2 | `docs/epic3/INPUT_ARTIFACTS_CHECKLIST.md` | Task 3.0.2 — Chốt input artifacts từ EPIC 2 |
| 3 | `docs/epic3/DELIVERABLES_LIST.md` | Task 3.0.3 — Chốt output deliverables cuối cùng |
| 4 | `docs/epic3/session_reports/phien1_report.md` | Báo cáo nghiệm thu phiên này |

---

## 3. Các điểm CẦN XÁC NHẬN trước Phiên 2

### Nghiêm trọng — Cần trước khi Feature 3.1 bắt đầu

1. **`handoff_to_epic3.md`** — File này không tồn tại trong repo. Đây là tài liệu bắt buộc để Feature 3.1 bắt đầu validate artifacts. Cần yêu cầu EPIC 2 tạo lại hoặc xác nhận đã bàn giao ở đâu.

2. **`model_card.md`** — File không tìm thấy trong repo. Cần cho trang Limitations & Responsible Use và slide bảo vệ. Cần xác nhận EPIC 2 đã tạo chưa.

3. **`residual_stats.json`** — File không tìm thấy trong repo. Cần cho trang Model Info (hiển thị residual distribution). Cần xác nhận EPIC 2 đã export chưa.

4. **`model_metrics.json`** — Tìm thấy tại `4.MODELS/4.2.evaluation/model_metrics.json` nhưng chưa xác nhận đây có phải artifact chính thức từ EPIC 2 bàn giao. Cần xác nhận và copy vào `artifacts/epic2/metrics/`.

### Ưu tiên cao — Trước khi Feature 3.2 bắt đầu

5. **Chuẩn hoá `artifacts/epic2/`** — Cần copy toàn bộ 18 artifacts từ `7.ML/7.10.model_packaging/package/` và SHAP assets từ `7.ML/7.9.explainability/` vào thư mục chuẩn `artifacts/epic2/` để Backend (Feature 3.2) không phụ thuộc đường dẫn dài và không ổn định.

---

## 4. Đề xuất tiếp theo cho Phiên 2

**Task 3.0.4 — Chốt API contract**

API contract là cầu nối giữa FastAPI backend và Streamlit frontend. Phiên 2 nên chốt trước khi bắt đầu code backend hoặc frontend, để 2 team có thể làm việc song song:

1. Định nghĩa chi tiết request/response body cho từng endpoint (`/predict`, `/explain`, `/what-if`) — dựa trên `input_schema.json` và `output_schema.json` đã có.
2. Quyết định base URL của FastAPI (mặc định `http://localhost:8000`) và cách Streamlit gọi (hardcode vs env var).
3. Quyết định error response format thống nhất.
4. Quyết định SHAP assets format cho `/explain` — trả về JSON hay base64 image?
5. Xác nhận `artifact_artifact_path` sẽ là absolute path hay relative path từ working directory.

---

## 5. Ghi chú thêm

- Pipeline inference đã có sẵn method `predict_popularity(dict_record)` — backend chỉ cần gọi, không cần viết lại logic.
- 18 input fields đã được định nghĩa chi tiết trong `input_schema.json` với min/max/default/enforcement level — frontend form có thể dùng trực tiếp để generate validation.
- SHAP assets tồn tại đầy đủ (background, values, plots, samples) — backend `/explain` cần load và trả về cho frontend render.
