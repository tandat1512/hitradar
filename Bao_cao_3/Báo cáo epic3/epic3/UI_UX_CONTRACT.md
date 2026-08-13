# UI/UX CONTRACT — EPIC 3: HitRadar Pro Streamlit Frontend
**Ngày chốt:** 2026-07-30
**Phiên:** 3
**Người phụ trách:** Minh
**Nguồn tham chiếu:** `docs/epic3/API_CONTRACT.md`, `docs/epic3/DELIVERABLES_LIST.md`

---

## Tổng quan thiết kế

- **Framework:** Streamlit multi-page app
- **Layout:** Sidebar điều hướng (st.navigation hoặc pages/)
- **API Base URL:** configurable qua `API_BASE_URL` env var hoặc sidebar text_input
- **Theme:** Light mode mặc định; gợi ý Spotify-style (dark green accent, trắng/nền sáng)
- **Font tiếng Việt:** hỗ trợ Unicode đầy đủ

### Common UI States (áp dụng cho mọi trang có gọi API)

| Trạng thái | Xử lý UI |
|------------|----------|
| **Đang gọi API** | `st.spinner("Đang xử lý...")` + disable nút submit |
| **Thành công** | Hiển thị kết quả bình thường |
| **Lỗi 422 (validation)** | `st.error()` với message: `"Giá trị không hợp lệ: " + detail.message` — KHÔNG hiển thị traceback |
| **Lỗi 400 (bad JSON)** | `st.error("Yêu cầu không hợp lệ. Vui lòng thử lại.")` |
| **Lỗi 500** | `st.error("Lỗi server. Model có thể chưa sẵn sàng.")` |
| **API không phản hồi** | `st.warning("Không thể kết nối API. Kiểm tra backend đang chạy.")` |
| **Model degraded (/health trả degraded)** | Banner cảnh báo ở đầu trang: `"⚠️ Model chưa sẵn sàng. Một số chức năng có thể không hoạt động."` |

---

## Trang: Home / Project Overview

### Mục đích
Giới thiệu tổng quan dự án HitRadar Pro, giúp người dùng hiểu dự án làm gì trước khi thử tính năng.

### Thành phần UI chính

1. **Hero section**
   - Tiêu đề: "HitRadar Pro — Dự đoán Popularity của bài hát Spotify"
   - Mô tả ngắn (2-3 câu): bài toán, dataset (586K tracks, 1921–2020), model XGBoost
   - Nút/liên kết: "Dự đoán ngay" → chuyển sang trang Predict

2. **Thống kê nhanh (KPIs)**
   - Số bài hát trong dataset: "586,672"
   - Khoảng năm: "1921–2020"
   - Số artists: "1,162,095"
   - Model: "XGBoost" (lấy từ `/model-info.model_family`)
   - Nguồn dữ liệu: "Spotify Audio Features & Metadata"
   - *(Dữ liệu KPI là static, không gọi API)*

3. **Mô tả workflow (3 bước)**
   - Bước 1: Nhập thông số bài hát (Predict Popularity)
   - Bước 2: Xem giải thích tại sao model đưa ra kết quả đó (SHAP Explanation)
   - Bước 3: Thử thay đổi thông số để xem kết quả thay đổi ra sao (What-If Simulator)

4. **Navigation cards** (5 cards dẫn đến 5 trang chính)
   - 🎯 Dự đoán Popularity
   - 📊 Giải thích SHAP
   - 🔄 What-If Simulator
   - 📈 Xu hướng Music 1921–2020
   - ℹ️ Thông tin Model

### Luồng thao tác
1. User mở app → thấy Overview
2. Đọc giới thiệu → click navigation card hoặc sidebar → chuyển trang
3. Không cần tương tác gì phức tạp ở trang này

### Trạng thái đặc biệt
- Không gọi API ở trang này
- Nếu `/health` trả degraded → hiển thị banner cảnh báo ở đầu trang

---

## Trang: Predict Popularity

### Mục đích
Cho phép người dùng nhập thông số bài hát và nhận kết quả dự đoán popularity từ model.

### Thành phần UI chính

1. **Tiêu đề:** "Dự đoán Popularity"

2. **Sidebar: Cấu hình**
   - `API_BASE_URL`: `st.text_input("API URL", value="http://localhost:8000")`
   - `st.checkbox("Dùng giá trị mặc định")` → điền form bằng example_input
   - Nút "Test kết nối" → gọi `GET /health`, hiển thị status badge

3. **Form nhập liệu** (18 fields, theo đúng thứ tự API contract)
   - **Nhóm Metadata:**
     - `release_year`: `st.number_input("Năm phát hành", min_value=1921, max_value=2020, value=2000, step=1)
     - `release_month`: `st.number_input("Tháng phát hành", min_value=1, max_value=12, value=6, step=1)`
     - `decade`: `st.selectbox("Thập kỷ", options=[1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020])`
     - `release_precision`: `st.selectbox("Độ chính xác ngày", options=["day", "month", "year"])`
     - `explicit`: `st.checkbox("Explicit (nội dung nhạy cảm)")`

   - **Nhóm Audio Features (0–1):**
     - `danceability`: `st.slider("Danceability", 0.0, 1.0, 0.5, 0.01)` — mô tả: "Nhịp điệu và khả năng nhảy"
     - `energy`: `st.slider("Energy", 0.0, 1.0, 0.5, 0.01)` — mô tả: "Cường độ và mạnh mẽ"
     - `valence`: `st.slider("Valence", 0.0, 1.0, 0.5, 0.01)` — mô tả: "Mức độ tích cực / vui vẻ"
     - `speechiness`: `st.slider("Speechiness", 0.0, 1.0, 0.1, 0.01)` — mô tả: "Tỷ lệ lời nói"
     - `acousticness`: `st.slider("Acousticness", 0.0, 1.0, 0.3, 0.01)` — mô tả: "Âm thanh acoustic"
     - `instrumentalness`: `st.slider("Instrumentalness", 0.0, 1.0, 0.1, 0.01)` — mô tả: "Không có lời"
     - `liveness`: `st.slider("Liveness", 0.0, 1.0, 0.15, 0.01)` — mô tả: "Hiệu ứng khán giả trực tiếp"

   - **Nhóm Technical:**
     - `duration_min`: `st.number_input("Thời lượng (phút)", min_value=0.0, max_value=120.0, value=3.5, step=0.1)`
     - `loudness`: `st.slider("Loudness (dB)", -60.0, 0.0, -10.0, 0.5)` — mô tả: "Âm lượng tổng thể (dB)"
     - `tempo`: `st.slider("Tempo (BPM)", 0.0, 300.0, 120.0, 1.0)` — mô tả: "Nhịp độ tính bằng BPM"
     - `key`: `st.selectbox("Key (Cung âm)", options=range(12), format_func=lambda x: ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"][x])`
     - `mode`: `st.radio("Mode", options=[1, 0], format_func=lambda x: "Major (Vui)" if x == 1 else "Minor (Buồn)")`
     - `time_signature`: `st.selectbox("Time Signature", options=[4.0, 3.0, 5.0, 1.0], format_func=lambda x: f"{int(x)}/4")`

4. **Nút hành động**
   - `"🔮 Dự đoán"` (primary button): gọi `POST /predict`
   - `"↻ Đặt lại"`: reset form về giá trị mặc định
   - `"💾 Dùng làm baseline (What-If)"`: lưu current form state vào session_state, chuyển sang What-If với pre-filled data

5. **Khu vực kết quả** (hiện khi có response)
   - **Gauge/Big number:** `prediction_display` hiển thị to, màu theo ngưỡng:
     - 0–30: đỏ/cam ("Thấp")
     - 31–60: vàng/xanh nhạt ("Trung bình")
     - 61–100: xanh lá ("Cao")
   - **Chi tiết:** `prediction_raw` (2 chữ số thập phân), `prediction_clipped` (2 chữ số thập phân)
   - **Warnings:** nếu có warnings → `st.warning()` liệt kê
   - **Metadata nhỏ:** model_id, model_version ở góc dưới

### Luồng thao tác
1. User điền form (hoặc click "Dùng giá trị mặc định")
2. Click "Dự đoán"
3. Spinner hiện → API response
4. Kết quả hiển thị (gauge + chi tiết)
5. User click "Dùng làm baseline" → chuyển sang What-If Simulator với dữ liệu vừa nhập
6. User click SHAP Explanation → chuyển sang trang SHAP với dữ liệu vừa nhập

### Trạng thái loading/error
- Loading: spinner + disable button
- Error 422: `st.error(f"Giá trị không hợp lệ: {detail['message']}")` — không hiện traceback
- Error 500: `st.error("Lỗi server. Model có thể chưa sẵn sàng.")`
- Network error: `st.warning("Không thể kết nối API.")`
- Warnings: `st.warning()` với nội dung từ response.warnings

---

## Trang: SHAP Explanation

### Mục đích
Giải thích tại sao model đưa ra dự đoán đó — mỗi feature đóng góp bao nhiêu vào kết quả cuối cùng.

### Thành phần UI chính

1. **Tiêu đề:** "Giải thích SHAP"

2. **Data input section** (2 cách nhập)
   - **Cách A:** Dùng lại dữ liệu từ Predict (đã lưu trong `session_state`)
     - Hiển thị: `"Dùng dữ liệu từ trang Dự đoán"` + badge
     - Nút "Sử dụng" → dùng `session_state.last_prediction_input`
   - **Cách B:** Nhập trực tiếp form (giống hệt form ở trang Predict)
     - Collapse section "Nhập thủ công"

3. **Nút "Phân tích SHAP"** → gọi `POST /explain`

4. **Kết quả SHAP**

   a. **Summary bar** (top features ảnh hưởng nhất)
      - Horizontal bar chart với 5 bars (từ `top_features`)
      - Màu: xanh lá cho SHAP > 0 (tăng popularity), đỏ cho SHAP < 0 (giảm popularity)
      - Label: tên feature + giá trị SHAP + giá trị thực của feature
      - Tooltip: giải thích ngắn ý nghĩa feature đó

   b. **SHAP Summary Beeswarm** (nếu có plot từ `/model-info` hoặc asset)
      - Hiển thị `shap_summary_beeswarm.png` (từ SHAP assets) hoặc vẽ từ dữ liệu
      - Caption: "Biểu đồ Beeswarm — mỗi điểm là một bài hát. Màu xanh = giá trị thấp, đỏ = giá trị cao."

   c. **Bảng chi tiết đầy đủ**
      - `st.dataframe` với 2 cột: Tên feature | Giá trị SHAP
      - Sắp xếp theo abs(SHAP) giảm dần
      - Highlight dòng top 5

   d. **Base value + Prediction breakdown**
      - Text: `base_value = 42.15`
      - Text: `prediction = base_value + Σ SHAP_values`
      - Text: `46.42 = 42.15 + (+2.34) + (-0.92) + ...`

   e. **Predicted popularity card** (nhỏ)
      - Hiển thị `prediction_display` đã được dự đoán

5. **Chart captions**
   - Mỗi chart có caption 1-2 câu giải thích ý nghĩa
   - Ví dụ: "Release Year có ảnh hưởng mạnh nhất — bài hát gần đây hơn thường có popularity cao hơn."

### Luồng thao tác
1. User đến trang từ Predict (có sẵn data) hoặc nhập thủ công
2. Click "Phân tích SHAP"
3. Spinner → hiển thị chart + table
4. User hover chart để xem chi tiết
5. User có thể quay lại Predict để điều chỉnh input

### Trạng thái loading/error
- Giống trang Predict — spinner + disable button + error handling
- Nếu `/explain` trả 500: `st.error("Tính năng giải thích SHAP tạm thời không khả dụng.")`
- Nếu SHAP assets không load được: hiển thị table (fallback), ẩn chart

---

## Trang: What-If Simulator

### Mục đích
Cho phép người dùng thay đổi một hoặc nhiều features và xem prediction thay đổi như thế nào theo thời gian thực.

### Thành phần UI chính

1. **Tiêu đề:** "What-If Simulator"

2. **Baseline section**
   - Nếu có từ Predict: hiển thị "Baseline" badge + các giá trị đã dùng
   - Nếu không có: hiển thị form baseline điền đầy đủ 18 fields (giống Predict)
   - Nút "Dùng baseline hiện tại" → submit baseline

3. **Điều khiển thay đổi** — 2 chế độ

   **Chế độ A: Scenario presets (nhanh)**
   - `st.selectbox("Chọn kịch bản", options=[
     "— Chọn kịch bản —",
     "Tăng Energy lên 0.9",
     "Giảm Acousticness xuống 0.1",
     "Đổi sang Major Mode",
     "Tăng Tempo lên 150 BPM",
     "Tăng Danceability + Valence",
     "Custom (tùy chỉnh)"
   ])`
   - Kịch bản được định nghĩa sẵn → tự điền vào `changed_features`

   **Chế độ B: Custom sliders**
   - Chỉ hiện 6-8 features được chọn làm "điều khiển":
     - `danceability`, `energy`, `valence`, `acousticness`, `tempo`, `loudness`, `release_year`, `explicit`
   - Mỗi feature: slider kèm giá trị hiện tại (baseline) và giá trị mới
   - Checkbox "Bật thay đổi" cho từng feature (mặc định off)
   - `[st.checkbox] [feature_name]: [slider] (baseline: X → new: Y)`

4. **Nút "Cập nhật so sánh"** → gọi `POST /what-if`

5. **Khu vực kết quả so sánh**

   a. **Prediction comparison cards**
      - Card "Before": `prediction_display` với baseline, nền xám
      - Card "After": `prediction_display` với changed features, nền xanh
      - Card "Thay đổi": `delta_display` (+/- số điểm), màu xanh nếu tăng, đỏ nếu giảm

   b. **Visual comparison bar**
      - Horizontal bar chart: before bar + after bar cạnh nhau
      - Ghi chú: "Thay đổi: +8 điểm" hoặc "-5 điểm"

   c. **Changes applied list**
      - `st.markdown("**Các thay đổi:**")`
      - Bảng: Feature | Baseline | Mới | Thay đổi

   d. **Quick action buttons**
      - "Áp dụng làm baseline mới" → cập nhật baseline
      - " Quay lại kịch bản gốc" → reset changed features
      - "↗ Đi đến SHAP Explanation" → chuyển trang SHAP với changed features

### Luồng thao tác
1. User đến từ Predict (baseline đã có) hoặc nhập baseline mới
2. Chọn preset HOẶC bật custom sliders
3. Click "Cập nhật so sánh"
4. Spinner → hiển thị cards + chart so sánh
5. User điều chỉnh tiếp → click lại → kết quả cập nhật
6. User click "Áp dụng làm baseline mới" → tiếp tục thử nghiệm

### Trạng thái loading/error
- Giống trang Predict
- Error 422 (changed_features field không hợp lệ): `st.error("Field không hợp lệ. Vui lòng kiểm tra lại.")`
- Nếu không có baseline: `st.warning("Vui lòng nhập baseline trước.")`

---

## Trang: Music Trends 1921–2020

### Mục đích
Cho thấy xu hướng thay đổi của âm nhạc theo thời gian — giúp user hiểu dataset và tại sao model học được pattern.

### Thành phần UI chính

*(Ghi chú: dữ liệu trend được chuẩn bị ở Feature 3.4 từ database analytics views. Trang này chỉ hiển thị, không gọi model API.)*

1. **Tiêu đề:** "Xu hướng Âm nhạc 1921–2020"

2. **Bộ lọc**
   - `st.selectbox("Biểu đồ theo": ["Thập kỷ", "Năm"])`
   - `st.selectbox("Genre lọc": ["Tất cả", "Pop", "Rock", "Hip-Hop", "Electronic", "Jazz"])` *(tùy chọn, có thể bỏ qua)*

3. **Các biểu đồ**

   a. **Popularity trung bình theo thập kỷ**
      - Line chart: decade (trục X) → avg popularity (trục Y)
      - Màu: Spotify green accent
      - Ghi chú: "Popularity trung bình tăng mạnh từ 2000s trở đi."

   b. **Audio Features Trends**
      - Line chart đa series: danceability, energy, valence, acousticness theo decade
      - Mỗi feature 1 màu
      - Ghi chú: "Danceability và Energy tăng đều từ 1970s."

   c. **Explicit content theo thập kỷ**
      - Bar chart: tỷ lệ bài hát explicit theo decade
      - Ghi chú: "Tỷ lệ explicit tăng mạnh từ 1990s."

   d. **Duration trend**
      - Line chart: thời lượng trung bình (phút) theo decade
      - Ghi chú: "Bài hát ngắn hơn qua các thập kỷ, trung bình 3–5 phút."

   e. **Top Artists / Genres** (tùy chọn)
      - Bar chart: top 10 artists hoặc genres theo số bài hát
      - Ghi chú: ngắn gọn mỗi chart

4. **Chart captions** (mỗi chart ≥ 1 caption giải thích insight)
5. **Data source note:** `"Dữ liệu từ Spotify Dataset, phân tích trong EPIC 1"`

### Luồng thao tác
1. User mở trang → biểu đồ hiển thị ngay (dữ liệu static từ Feature 3.4)
2. User thay đổi bộ lọc → chart cập nhật
3. User hover chart → xem chi tiết từng điểm

### Trạng thái đặc biệt
- Không gọi model API
- Nếu Feature 3.4 chưa chạy: hiển thị `st.info("Dữ liệu trend đang được chuẩn bị...")`

---

## Trang: Model Info

### Mục đích
Giới thiệu thông tin kỹ thuật của model: version, metrics, feature importance, giới hạn.

### Thành phần UI chína

1. **Tiêu đề:** "Thông tin Model"

2. **Metadata card**
   - Gọi `GET /model-info`
   - Hiển thị table:
     - `model_id`: "EXP24-XGB-FINAL-001"
     - `model_version`: "1.0.0"
     - `model_family`: "XGBoost"
     - `package_version`: "2.7.0"
     - `data_version`: "1.0.0"
     - `feature_set`: "FS23-SELECTED"
     - `training_date`: "2026-07-20" *(hoặc "—" nếu null)*

3. **Metrics card**
   - Hiển thị MAE, RMSE, R2 từ `GET /model-info.metrics`
   - Nếu metrics null: hiển thị `"Metrics đang được cập nhật..."`
   - Format:
     - MAE: "14.23 điểm" (2 decimal)
     - RMSE: "18.75 điểm" (2 decimal)
     - R²: "0.41" (2 decimal, không có đơn vị)

4. **Feature Importance chart**
   - Gọi `GET /model-info` hoặc load `shap_global_importance_selected.png`
   - Bar chart ngang: top 15 features theo SHAP importance
   - Ghi chú: "Top features ảnh hưởng nhất đến popularity dự đoán."

5. **Training overview**
   - Text block:
     - Số features: "31 selected features (từ 18 input)"
     - Dataset: "586,672 tracks"
     - Split: "Temporal split (train → validation → test)"

6. **Model architecture card**
   - Text block:
     - Algorithm: XGBoost Regressor
     - Feature engineering: 18 → 31 features (interaction terms, cyclical encoding)
     - Preprocessing: imputation, scaling
     - *(Chi tiết từ technical appendix)*

### Luồng thao tác
1. User mở trang → gọi `/model-info`
2. Metadata + metrics hiển thị
3. Feature importance chart render
4. User scroll xuống xem chi tiết

### Trạng thái đặc biệt
- Nếu `/model-info` trả 500: `st.error("Không thể tải thông tin model.")`
- Nếu metrics null: `st.info("Metrics đang được cập nhật từ EPIC 2.")`

---

## Trang: Limitations & Responsible Use

### Mục đích
Trang tĩnh giáo dục người dùng về giới hạn của model và cách sử dụng có trách nhiệm.

### Thành phần UI chính

*(Nội dung tĩnh — không gọi API)*

1. **Tiêu đề:** "Giới hạn & Sử dụng có trách nhiệm"

2. **Section: Giới hạn của Dataset**
   - **Khoảng thời gian:** "Dataset chỉ bao gồm bài hát từ 1921–2020. Model không dự đoán được popularity cho bài hát mới hơn 2020."
   - **Nguồn metadata:** "Spotify popularity score không phải thước đo chất lượng nghệ thuật — nó phản ánh mức độ phổ biến trên nền tảng."
   - **Survivorship bias:** "Dataset thiên lệch về các bài hát đã được ghi nhận — bài hát ít phổ biến có thể không được thu thập đầy đủ."

3. **Section: Giới hạn của Model**
   - **Underprediction:** "Model có xu hướng đánh giá thấp các viral tracks — bài hát bất ngờ nổi tiếng nằm ngoài pattern thông thường."
   - **High error on outliers:** "Bài hát có popularity rất cao (>80) hoặc rất thấp (<10) có error rate cao hơn trung bình."
   - **Temporal shift:** "Xu hướng âm nhạc thay đổi theo thời gian — model được train trên dữ liệu quá khứ, có thể kém chính xác cho xu hướng tương lai."
   - **Không phải đề xuất:** "Model không đưa ra lời khuyên âm nhạc. Đây là công cụ phân tích, không phải tư vấn nghệ thuật."

4. **Section: Cách sử dụng có trách nhiệm**
   - ✅ Dùng để hiểu các yếu tố ảnh hưởng đến popularity trong dataset
   - ✅ Dùng để phân tích xu hướng lịch sử
   - ✅ Tham khảo cho nghiên cứu học thuật
   - ❌ Không dùng để quyết định phát hành nhạc
   - ❌ Không dùng để đánh giá chất lượng nghệ thuật
   - ❌ Không dùng cho bài hát ngoài khoảng 1921–2020

5. **Section: Credits**
   - Dataset: "Spotify Audio Features Dataset (Kaggle)"
   - Model: "XGBoost — huấn luyện trong EPIC 2"
   - Packaging: "HitRadar Pro EPIC 3"

6. **Link đến Model Card** *(nếu artifact tồn tại)*
   - `st.markdown("[📄 Xem chi tiết Model Card](link_to_model_card)")

### Luồng thao tác
- Trang tĩnh — user đọc và scroll
- Không cần tương tác phức tạp

### Trạng thái đặc biệt
- Không gọi API
- Nếu không có model_card.md: hiển thị nội dung mặc định từ mô tả trên

---

## Sidebar Navigation

Mọi trang đều có sidebar thống nhất:

```
[Logo/Icon: 🎵 HitRadar Pro]

Navigation:
  🏠 Home
  🎯 Predict
  📊 SHAP Explanation
  🔄 What-If Simulator
  📈 Music Trends
  ℹ️ Model Info
  ⚠️ Limitations

---
Cấu hình:
  API URL: [http://localhost:8000]
  [Test kết nối] → badge: ✅ healthy / ❌ degraded

---
Model: XGBoost v1.0.0
```

---

## Design Principles

| Nguyên tắc | Mô tả |
|------------|--------|
| **Consistent** | Mọi trang dùng cùng sidebar, header style, color palette |
| **Progressive disclosure** | Form Predict cho thấy tất cả 18 fields; What-If ẩn advanced options |
| **Graceful degradation** | Mọi lỗi API hiển thị message rõ ràng, không crash app |
| **Vietnamese-first** | Tất cả labels, messages, buttons bằng tiếng Việt |
| **No technical jargon on UI** | User không cần biết "SHAP", "XGBoost" — chỉ thấy kết quả |
