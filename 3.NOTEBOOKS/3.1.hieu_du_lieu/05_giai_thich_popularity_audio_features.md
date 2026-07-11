# 05 — Giải thích Popularity và Audio Features

> Nguồn: `NB02/03/06 executed output`, `EDA_INSIGHTS_REPORT.md`, `ANALYTICS_VIEWS_REPORT.md`

---

## Popularity là gì?

**Popularity** là điểm từ **0 đến 100** do Spotify tính, phản ánh **mức độ được stream gần đây** — không phải chất lượng bài hát, không phải đánh giá của người nghe.

- 0 = gần như không ai stream trong thời gian gần đây
- 100 = đang được stream rất nhiều (hit hiện tại)

Trong dataset HitRadar, cột này xuất hiện dưới 2 tên:
- `popularity` — trong `vw_tracks_overview`
- `target_popularity` — trong `vw_ml_training_dataset` (cùng giá trị, tên khác để nhắc đây là label)

---

## Vì sao popularity là target/label?

Mục tiêu ML của HitRadar: **dự đoán một bài hát sẽ nổi tiếng đến mức nào**.

→ `target_popularity` là thứ model cần **dự đoán** (output), không phải thứ model dùng để dự đoán (input).

Tương tự như bài toán dự đoán giá nhà: giá nhà là label, diện tích/phòng ngủ là features.

---

## Vì sao không dùng target_popularity làm input?

Nếu dùng popularity làm input feature để dự đoán popularity → model học `popularity ≈ popularity` → accuracy 100% nhưng **vô nghĩa hoàn toàn**.

Đây gọi là **target leakage** — một trong những lỗi nghiêm trọng nhất trong ML.

---

## Vì sao popularity bị lệch thấp?

Phân bố thực tế từ `vw_popularity_stats` (NB02):

| Bucket | Số tracks | Tỷ lệ |
|--------|-----------|-------|
| 0–20 | 219,988 | 37.5% |
| 21–40 | 219,003 | 37.3% |
| 41–60 | 122,813 | 20.9% |
| 61–80 | 24,132 | 4.1% |
| 81–100 | 736 | 0.1% |

**75% bài hát có popularity ≤ 40.** Chỉ 736 bài (0.1%) đạt trên 80.

Nguyên nhân: trên Spotify có hàng triệu bài, phần lớn ít được nghe. Chỉ một thiểu số nhỏ là hit. Đây là phân bố tự nhiên, không phải lỗi data.

Thêm: **44,690 bài có popularity = 0** (7.6%) — tồn tại trên Spotify nhưng không ai stream gần đây.

---

## Vì sao release_year tương quan cao với popularity?

Correlation = **+0.5909** (mạnh nhất, NB06).

Spotify tính popularity dựa trên **streams trong khoảng thời gian gần đây** (ước tính ~28 ngày). Hệ quả:

- Bài phát hành 2021 → nhiều người đang stream → score cao
- Bài phát hành 1970 → dù hay, ít ai stream lại → score thấp

Avg popularity theo thập kỷ (NB02):
- 1920s: **1.14**
- 2020s: **41.74**

Đây là **time bias** — không phải vì nhạc mới hay hơn, mà vì cách Spotify tính điểm.

---

## Audio Features — giải thích từng feature

Tất cả audio features dưới đây do Spotify tính bằng thuật toán phân tích âm thanh, không phải metadata do người nhập.

---

### danceability

| | |
|---|---|
| **Ý nghĩa** | Bài hát phù hợp để nhảy theo không? |
| **Giá trị** | 0.0 (không danceable) → 1.0 (rất danceable) |
| **Mean** | 0.564 (NB03) |
| **Rủi ro ML** | Thấp — phân bố đều, dùng được trực tiếp. Corr với popularity: +0.19 |

---

### energy

| | |
|---|---|
| **Ý nghĩa** | Mức năng lượng/cường độ — bài mạnh, dồn dập hay nhẹ nhàng? |
| **Giá trị** | 0.0 (nhẹ) → 1.0 (mạnh) |
| **Mean** | 0.542 (NB03) |
| **Rủi ro ML** | Thấp — phân bố rộng, phù hợp ML. Corr: +0.30. Tăng theo thời gian (1950s→2020s). |

---

### speechiness

| | |
|---|---|
| **Ý nghĩa** | Mức độ có lời nói (rap, podcast, spoken word) |
| **Giá trị** | 0.0 (thuần nhạc) → 1.0 (thuần nói) |
| **Mean / Median** | 0.105 / **0.044** (NB03) — lệch phải nặng |
| **Rủi ro ML** | **Cao** — zero-inflated, cần log-transform ở EPIC 2. Corr: -0.05 (yếu). |

---

### acousticness

| | |
|---|---|
| **Ý nghĩa** | Mức độ acoustic (guitar thùng, piano không khuếch đại) |
| **Giá trị** | 0.0 (điện tử/studio) → 1.0 (thuần acoustic) |
| **Mean** | 0.450 (NB03) — bimodal (acoustic vs non-acoustic) |
| **Rủi ro ML** | **Trung bình** — giảm mạnh theo thời gian (0.90→0.28), confounded với release_year. Corr: -0.37. |

---

### instrumentalness

| | |
|---|---|
| **Ý nghĩa** | Mức độ nhạc không lời (không có vocal) |
| **Giá trị** | 0.0 (có lời) → 1.0 (thuần nhạc cụ) |
| **Mean / Median** | 0.114 / **0.000** (NB03) — hơn 50% bài = 0 |
| **Rủi ro ML** | **Cao** — zero-inflated, cần log-transform. Corr: -0.24. |

---

### liveness

| | |
|---|---|
| **Ý nghĩa** | Có nghe như live concert không? |
| **Giá trị** | 0.0 (studio) → 1.0 (live) |
| **Mean / Median** | 0.214 / 0.139 (NB03) |
| **Rủi ro ML** | Thấp — lệch phải nhẹ. Corr: -0.05 (yếu). |

---

### valence

| | |
|---|---|
| **Ý nghĩa** | Cảm xúc — vui/hạnh phúc (cao) hay buồn/tức giận (thấp) |
| **Giá trị** | 0.0 (buồn) → 1.0 (vui) |
| **Mean** | 0.552 (NB03) — phân bố đều |
| **Rủi ro ML** | Thấp về phân bố, nhưng **corr ≈ 0** với popularity — ít giá trị dự báo. |

---

### tempo

| | |
|---|---|
| **Ý nghĩa** | Tốc độ bài hát (BPM — beats per minute) |
| **Giá trị** | Số thực dương (thường 60–200 BPM) |
| **NULL** | **328 tracks** (0.056%) — NB03 |
| **Rủi ro ML** | **Cần impute** trước khi train. Corr: +0.07 (yếu). |

---

### loudness

| | |
|---|---|
| **Ý nghĩa** | Âm lượng tổng thể (dB) — thường âm (ví dụ -5 dB) |
| **Giá trị** | Thường từ -60 đến 0 dB |
| **Outlier** | 219 tracks có loudness > 0 dB (hiếm, hợp lệ) |
| **Rủi ro ML** | Trung bình — corr +0.33 nhưng confounded với release_year (nhạc mới to hơn). |

---

### time_signature

| | |
|---|---|
| **Ý nghĩa** | Nhịp điệu — thường 3, 4, hoặc 5 (ví dụ 4/4) |
| **Giá trị** | Số nguyên (3, 4, 5, 7...) |
| **NULL** | **337 tracks** (0.057%) — NB03 |
| **Rủi ro ML** | **Cần impute** (mode) trước khi train. Không có correlation report riêng. |

---

## Bảng tổng hợp rủi ro ML

| Feature | Corr với popularity | Phân bố | Rủi ro | Hành động EPIC 2 |
|---------|-------------------|---------|--------|-----------------|
| release_year | +0.59 | — | **Cao** (time bias) | Temporal split |
| loudness | +0.33 | Bình thường | Trung bình | Scale |
| energy | +0.30 | Đều | Thấp | Scale |
| acousticness | -0.37 | Bimodal | Trung bình | Scale, kiểm tra confounding |
| danceability | +0.19 | Đều | Thấp | Scale |
| instrumentalness | -0.24 | Zero-inflated | Cao | Log-transform |
| speechiness | -0.05 | Zero-inflated | Cao | Log-transform |
| valence | ≈0 | Đều | Thấp | Có thể bỏ |
| tempo | +0.07 | Có NULL | Trung bình | Impute + scale |
| time_signature | — | Có NULL | Trung bình | Impute |
| duration_min | +0.03 | Ổn định | Thấp | Scale |
| **target_popularity** | — | Lệch thấp | **Label** | **KHÔNG dùng làm input** |

*Nguồn correlation: NB06 executed output (`CORR()` trên `vw_ml_training_dataset`).*
