# 06 — Câu hỏi tự kiểm tra hiểu dữ liệu

> Nguồn đáp án: `EDA_INSIGHTS_REPORT.md`, `ANALYTICS_VIEWS_REPORT.md`, notebooks executed output

---

## Mức 1 — Cơ bản

### 1. Dataset có bao nhiêu tracks?

**Đáp án:** **586,672 tracks** trong `clean.tracks` và `vw_tracks_overview`.

---

### 2. Popularity là input hay target?

**Đáp án:** **Target (label).** Trong `vw_ml_training_dataset` gọi là `target_popularity`. Không dùng làm input feature — sẽ gây target leakage.

---

### 3. Genre lấy từ đâu?

**Đáp án:** Genre gắn vào **artist**, không gắn trực tiếp vào track. Đường đi: `track → track_artists → artist → artist_genres → genre`.

---

### 4. Vì sao cần analytics views?

**Đáp án:** Clean tables chứa raw rows (586K tracks). Analytics views **tổng hợp sẵn** (theo decade, bucket, genre trend) và **ML-safe** (`vw_ml_training_dataset`). EDA notebooks chỉ đọc views — không cần viết lại logic aggregate.

---

### 5. Data quality status hiện tại là gì?

**Đáp án:** **PASS_WITH_WARNINGS** — không có lỗi cấu trúc, có warnings về duration outliers, loudness, và track_artists coverage (96.54%).

---

## Mức 2 — Trung bình

### 6. Vì sao release_year có thể gây time bias?

**Đáp án:** Spotify tính popularity dựa trên streams **gần đây**. Bài mới tự nhiên có score cao hơn bài cũ — dù chất lượng không liên quan. Correlation = +0.59 (NB06). Model học release_year sẽ thiên vị nhạc mới.

---

### 7. Vì sao genre không nên one-hot toàn bộ 4,672 genres?

**Đáp án:** Tạo 4,672 cột sparse, phần lớn = 0. Gây overfitting trên genres hiếm, tốn memory (586K × 4,672), và không cân bằng được bias về top genres (rock, adult standards). Nên dùng top-N hoặc embedding.

---

### 8. Vì sao phải carry-forward warnings từ Feature 1.5?

**Đáp án:** Warnings (duration short=26, long=83, loudness>0=219, coverage=96.54%) **không phải lỗi** nhưng **ảnh hưởng ML strategy**. Nếu không ghi nhận, EPIC 2 có thể train model mà không biết 7.6% bài có popularity=0, hoặc 3.46% bài thiếu artist info.

---

### 9. Vì sao vw_genre_trends chỉ có 4,672 genres trong khi clean.genres có 5,366?

**Đáp án:** 694 genres thuộc artists bị skip trong track_artists coverage gap (96.54%). Những artists này không có track nào trong dataset → genre của họ không xuất hiện ở track-level analysis.

---

### 10. View nào có 12 rows và tại sao không phải lỗi?

**Đáp án:** `vw_tracks_by_decade` và `vw_explicit_by_decade` — mỗi view có 12 rows vì chỉ có 12 thập kỷ (1900s→2020s). Đây là data đã aggregate, không phải view rỗng.

---

## Mức 3 — Khó

### 11. Nếu split train/test random thì rủi ro gì?

**Đáp án:** **Future data leakage.** Train set có thể chứa bài 2020, test set chứa bài 1970. Model học release_year (+0.59 corr) → đoán đúng nhạc mới, sai nhạc cũ. Metric đẹp nhưng model không generalize. Cần **temporal split** (train = bài cũ, test = bài mới).

---

### 12. Nếu dùng artists.popularity làm feature thì leakage ra sao?

**Đáp án:** `artists.popularity` phản ánh mức độ nổi tiếng của **nghệ sĩ** — thông tin không có sẵn khi bài hát mới phát hành. Dùng nó để dự đoán `target_popularity` (popularity của bài) → model "nhìn trộm" thông tin tương lai. View `vw_top_artists` đặt tên cột là `artist_popularity_dashboard_only` để cảnh báo. `vw_ml_training_dataset` **không chứa** cột này.

---

### 13. Nếu join genre sai thì duplicate-weighting xảy ra thế nào?

**Đáp án:** Bài có 3 artists cùng genre "rock" → nếu `COUNT(*)` thay vì `COUNT(DISTINCT track_id)` → bài đó đếm **3 lần** cho genre "rock". Kết quả: track_count inflated, avg_popularity bị lệch (cùng bài được tính nhiều lần). `vw_genre_trends` dùng CTE `SELECT DISTINCT (track_id, genre_id, decade)` để tránh điều này.

---

### 14. Nếu xử lý popularity=0 sai thì ảnh hưởng model thế nào?

**Đáp án:** 44,690 bài (7.6%) có popularity=0 — không phải bài dở, mà bài bị lãng quên/inactive. Nếu **giữ nguyên**: model học rằng một nhóm lớn bài có score=0, có thể kéo prediction xuống. Nếu **xóa hết**: mất 7.6% data, bias về bài "active". Nếu **thay bằng giá trị khác** (impute): tạo fake signal. Cần quyết định chiến lược rõ ở EPIC 2 — không có đáp án duy nhất đúng.

---

### 15. Tại sao acousticness có correlation -0.37 nhưng không chắc là feature tốt?

**Đáp án:** Acousticness giảm mạnh theo thời gian (0.90→0.28 từ 1920s→2020s). Nhạc acoustic = nhạc cũ → popularity thấp (do time bias). Correlation âm có thể do **confounding với release_year**, không phải vì acousticness tự nó ảnh hưởng popularity. Cần kiểm tra thêm bằng partial correlation hoặc control release_year — *cần xác minh ở EPIC 2*.

---

## Cách dùng bộ câu hỏi này

- Trả lời được **mức 1** (5/5): hiểu cơ bản, có thể đọc notebooks
- Trả lời được **mức 2** (5/5): hiểu đủ để tham gia Feature 1.8
- Trả lời được **mức 3** (4/5 trở lên): sẵn sàng EPIC 2
