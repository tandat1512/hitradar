# Kịch bản Demo Dự án HitRadar (EPIC 3)

Tài liệu này mô tả kịch bản trình diễn (demo) chi tiết cho sản phẩm HitRadar (EPIC 3 - Model Serving & Web UI). Tổng thời gian dự kiến: **8 - 12 phút**.

## 1. Thông tin bài hát mẫu (Sample Input)

> **[GIẢ ĐỊNH — THAY BẰNG example_input.json THẬT KHI CÓ]**

Dưới đây là thông tin bài hát giả định được sử dụng xuyên suốt kịch bản demo:

- **Tên bài hát:** "Starboy" (feat. Daft Punk)
- **Nghệ sĩ:** The Weeknd
- **Thể loại (Genre):** Pop / R&B
- **Các đặc trưng âm thanh (Audio Features):**
  - Danceability: `0.679`
  - Energy: `0.715`
  - Key: `7` (G)
  - Loudness: `-7.093` dB
  - Mode: `1` (Major)
  - Speechiness: `0.276`
  - Acousticness: `0.141`
  - Instrumentalness: `0.000006`
  - Liveness: `0.137`
  - Valence: `0.486`
  - Tempo: `186.003` BPM
  - Duration: `230453` ms

---

## 2. Kịch bản Demo Chi tiết (8 - 12 phút)

### Bước 1: Mở trang Home & Giới thiệu dự án (1 phút)
- **Hành động:**
  - Mở trình duyệt, truy cập URL của ứng dụng Streamlit (ví dụ: `http://localhost:8501`).
  - Hiển thị trang chủ (Home Page).
- **Thuyết minh:**
  - Giới thiệu ngắn gọn mục tiêu của dự án HitRadar: Dự đoán mức độ phổ biến (popularity) của một bài hát trên Spotify dựa vào các đặc trưng âm thanh và học máy.
  - Chỉ ra 4 tính năng chính trên thanh sidebar: Home, Predict & Explain, What-If Simulator, Music Trends.
- **Dự phòng (Backup):**
  - Nếu frontend không tải được: Mở video ghi hình trước trang Home hoặc chụp màn hình slide thuyết trình.

### Bước 2: Vào trang Predict, nhập bài hát & Dự đoán (2 - 3 phút)
- **Hành động:**
  - Chuyển sang tab **Predict & Explain** trên sidebar.
  - Nhập (hoặc chọn từ dropdown nếu có load sẵn) bài hát "Starboy" với các thông số [GIẢ ĐỊNH] ở trên.
  - Bấm nút **"Predict Popularity"**.
  - Hiển thị kết quả dự đoán (Ví dụ: `Hit - 85/100`) kèm theo thanh tiến độ hoặc đồng hồ đo (Gauge Chart).
- **Thuyết minh:**
  - Giải thích cách hệ thống nhận input và gửi request tới FastAPI backend.
  - Nêu bật kết quả dự đoán (Hit/Non-Hit) và độ tin cậy.
- **Dự phòng (Backup):**
  - Nếu API backend chết (không trả về /predict): Trình bày kết quả JSON mẫu từ Postman hoặc Swagger UI (chạy offline).

### Bước 3: Xem SHAP Explanation cho kết quả dự đoán (2 phút)
- **Hành động:**
  - Cuộn xuống phần **"Why this result? (Model Explanation)"** ngay dưới kết quả dự đoán.
  - Hiển thị biểu đồ Waterfall SHAP.
- **Thuyết minh:**
  - Chỉ ra đặc trưng nào đóng góp nhiều nhất (ví dụ: `Danceability` cao làm tăng điểm Hit, `Liveness` làm giảm điểm).
  - Giải thích ngắn gọn SHAP giúp minh bạch hoá quyết định của mô hình AI như thế nào, tránh tình trạng "hộp đen".
- **Dự phòng (Backup):**
  - Nếu ảnh SHAP lỗi không render: Mở file ảnh `shap_waterfall_sample.png` đã lưu sẵn dưới local.

### Bước 4: Vào What-If Simulator (2 - 3 phút)
- **Hành động:**
  - Chuyển sang tab **What-If Simulator**.
  - Bài hát "Starboy" vẫn đang được chọn làm base.
  - Kéo thanh slider của `Energy` từ `0.715` xuống `0.4` và `Danceability` từ `0.679` xuống `0.3`.
  - Bấm nút **"Re-Predict"**.
  - Hiển thị kết quả mới (Điểm Popularity giảm mạnh, ví dụ còn 45/100).
- **Thuyết minh:**
  - Minh hoạ kịch bản: "Nếu bài hát này được phối lại (remix) với nhịp độ chậm hơn và ít năng lượng hơn, độ phổ biến sẽ giảm đáng kể".
  - Nhấn mạnh tính ứng dụng cho các producer/nhạc sĩ để điều chỉnh nhạc trước khi phát hành.
- **Dự phòng (Backup):**
  - Trình bày 2 ảnh chụp màn hình Trước và Sau khi kéo slider.

### Bước 5: Xem trang Music Trends (2 phút)
- **Hành động:**
  - Chuyển sang tab **Music Trends (EDA)**.
  - Hiển thị các biểu đồ tương tác (Scatter plot giữa Energy & Loudness, hoặc Bar chart thể loại).
- **Thuyết minh:**
  - Chỉ ra 1-2 insight nổi bật. Ví dụ: "Nhạc Pop có xu hướng Energy cao thường nằm trong Top Hit".
  - Cho thấy HitRadar không chỉ là công cụ dự đoán mà còn là dashboard phân tích thị trường âm nhạc.
- **Dự phòng (Backup):**
  - Nếu biểu đồ load chậm: Dùng slide báo cáo EDA từ EPIC 1 để thay thế.

### Bước 6: Xem Model Info & Kết thúc (1 - 2 phút)
- **Hành động:**
  - Cuộn xuống phần **Model Info & Limitations** (hoặc tab riêng).
  - Hiển thị các chỉ số hiệu suất của mô hình (F1-score, RMSE) và các hạn chế (ví dụ: chưa xét đến yếu tố fandom, marketing).
- **Thuyết minh:**
  - Khẳng định mô hình có độ tin cậy tốt nhưng vẫn nhận thức rõ các ranh giới và hạn chế.
  - Đóng lại buổi demo, cảm ơn và chuyển sang phần Hỏi & Đáp (Q&A).

---

## 3. Tổng hợp phương án dự phòng sự cố (Fallback Plan)

| Sự cố có thể xảy ra | Phương án xử lý |
| :--- | :--- |
| **Mất kết nối mạng / VPN** | Sử dụng toàn bộ dịch vụ ở dạng `localhost` (Backend: 8000, Frontend: 8501). Đã tải sẵn model weights offline. |
| **Backend API Crash (500 Error)**| Bật sẵn Postman với mock response trả về file JSON tĩnh mô phỏng kết quả. |
| **UI Streamlit bị treo / Load chậm** | Chuyển ngay sang thư mục `docs/epic3/demo_backups/` chứa video ghi màn hình MP4 (đã quay trước quá trình chạy thật). |
| **Lỗi render biểu đồ SHAP** | Mở thư mục ảnh tĩnh chứa các file PNG của biểu đồ SHAP và What-If. |
