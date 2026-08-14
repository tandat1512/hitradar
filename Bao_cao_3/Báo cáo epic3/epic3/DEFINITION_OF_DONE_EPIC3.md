# Definition of Done (DoD) - EPIC 3 (Model Serving & Web UI)

Tài liệu này định nghĩa các tiêu chí hoàn thành (Definition of Done) bắt buộc phải đạt được trước khi nghiệm thu EPIC 3. Tất cả các tiêu chí phải cụ thể, đo lường/kiểm chứng được (có/không hoặc có bằng chứng).

## 1. Artifact Validation
- [ ] File `MODEL_WEIGHTS.pkl` (hoặc định dạng tương đương) đã được load thành công vào bộ nhớ, không sinh lỗi trong log khởi động.
- [ ] File `preprocessor.pkl` (hoặc scaler/encoder) đã được áp dụng đúng chuẩn đầu vào, khớp 100% với định dạng dữ liệu huấn luyện của EPIC 2.

## 2. Backend (FastAPI)
- [ ] Endpoint `GET /health` trả về `{"status": "ok"}` hoặc tương đương với HTTP 200 dưới 50ms.
- [ ] Endpoint `POST /predict` trả về response chuẩn schema (Popularity Score, Hit/Non-Hit, SHAP values) với HTTP 200 trong thời gian dưới 500ms khi nhận input hợp lệ.
- [ ] Endpoint `POST /predict` bắt được lỗi (HTTP 422) và trả về thông báo lỗi rõ ràng nếu request body thiếu field hoặc sai kiểu dữ liệu.
- [ ] Backend được cấu hình log đầy đủ các request tới `/predict` (thời gian xử lý, trạng thái HTTP, lỗi nếu có).

## 3. Frontend (Streamlit)
- [ ] Giao diện Home hiển thị đầy đủ thông tin giới thiệu dự án, không có lỗi render markdown hoặc hình ảnh.
- [ ] Form nhập liệu trên trang Predict có đủ các trường input cho các đặc trưng (Energy, Danceability...), không bị tràn UI trên màn hình độ phân giải 1080p.
- [ ] Nút "Predict" khi bấm sẽ hiển thị trạng thái loading (spinner) trong khi chờ API phản hồi.
- [ ] Kết quả trả về (Score & Label) được hiển thị rõ ràng bằng số và màu sắc (Ví dụ: Xanh cho Hit, Đỏ cho Non-Hit).

## 4. Dashboard & Visualization
- [ ] Trang What-If Simulator có các thanh trượt (slider) cho phép thay đổi giá trị input, và nút Re-Predict cập nhật lại kết quả đúng logic.
- [ ] Biểu đồ SHAP Waterfall (hoặc Bar chart) được render thành công trên giao diện, hiển thị ít nhất Top 5 đặc trưng ảnh hưởng lớn nhất.
- [ ] Trang Music Trends (EDA) hiển thị ít nhất 2 biểu đồ tương tác (Plotly/Altair/Bokeh) mô tả phân phối dữ liệu hợp lệ mà không bị vỡ khung.

## 5. Integration & E2E Testing
- [ ] Streamlit gọi API backend qua biến môi trường hoặc config `API_URL`, không hardcode `localhost` ở cấp độ code lõi (có file `.env` hoặc config).
- [ ] Đã chạy thử ít nhất 3 kịch bản E2E: (1) Request hợp lệ -> Predict đúng, (2) Thay đổi slider -> Predict kết quả thay đổi, (3) Request API bị lỗi -> Frontend hiển thị toast/error cảnh báo người dùng.

## 6. Performance, Reliability & Demo Backup
- [ ] RAM tiêu thụ của cả Backend và Frontend chạy đồng thời không vượt quá 1.5 GB ở trạng thái nhàn rỗi.
- [ ] Đã quay 1 video demo màn hình (hoặc có bộ ảnh chụp UI đầy đủ) lưu tại `docs/epic3/demo_backups/` để dự phòng rủi ro khi demo trực tiếp.

## 7. Documentation
- [ ] Đã tạo đủ 8 file markdown theo quy định tại thư mục `docs/epic3/` (SCOPE, INPUT, DELIVERABLES, API, UI_UX, FRONTEND_DATA, DEMO_SCENARIO, DEFINITION_OF_DONE).
- [ ] File `README.md` ở thư mục gốc đã được cập nhật lệnh khởi chạy cho cả Backend (`uvicorn...`) và Frontend (`streamlit run...`).

## 8. Defense Preparation & Final Delivery
- [ ] Kịch bản trình bày (`DEMO_SCENARIO.md`) đã được review, đảm bảo thời lượng từ 8 đến 12 phút.
- [ ] Đã có báo cáo nghiệm thu của tất cả 4 phiên làm việc trong `docs/epic3/session_reports/`.
