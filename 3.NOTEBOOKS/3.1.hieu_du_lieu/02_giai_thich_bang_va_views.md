# 02 — Giải thích bảng và views

> Nguồn: `ANALYTICS_VIEWS_REPORT.md`, `EDA_INSIGHTS_REPORT.md`, `NB01 executed output`

---

## Ba tầng dữ liệu

### Raw layer — dữ liệu gốc

**Là gì?** Dữ liệu import trực tiếp từ file CSV Spotify, chưa qua xử lý.

**Dùng để trả lời:** "Dữ liệu gốc trông như thế nào trước khi clean?"

**Không nên hiểu sai:** Raw layer không dùng cho EDA hay ML. Notebooks Feature 1.7 **không đọc** từ đây.

---

### Clean layer — dữ liệu đã làm sạch

**Là gì?** Bảng PostgreSQL trong schema `clean`, đã qua pipeline Feature 1.4 (cleaning) và Feature 1.5 (quality gates). Đây là nguồn gốc của mọi analytics view.

**Dùng để trả lời:** "Dữ liệu chuẩn hoá cuối cùng trước khi tổng hợp là gì?"

**Không nên hiểu sai:** Clean layer không phải nơi EDA notebooks query trực tiếp — notebooks đọc từ analytics views.

---

### Analytics layer — views tổng hợp

**Là gì?** 10 views trong schema `analytics`, tạo từ clean layer ở Feature 1.6. Mỗi view trả lời một nhóm câu hỏi phân tích cụ thể.

**Dùng để trả lời:** "Tôi muốn phân tích X — query view nào?"

**Không nên hiểu sai:** Analytics views là **read-only**. Không sửa, không insert, không dùng làm bảng ghi dữ liệu mới.

---

## Clean tables

### `clean.tracks`

| | |
|---|---|
| **Là gì?** | Bảng trung tâm — mỗi dòng = 1 bài hát. **586,672 rows.** |
| **Dùng để trả lời** | Bài hát có những thuộc tính gì? Popularity, audio features, ngày phát hành? |
| **Không nên hiểu sai** | `popularity` ở đây là **label ML** — không dùng làm input feature. 71 tracks có `name IS NULL` (giữ theo rule F1.4). |

Cột quan trọng: `track_id`, `name`, `popularity`, `duration_ms`, `explicit`, `release_date`, `release_year`, `decade`, 7 audio features, `tempo`, `loudness`, `time_signature`.

---

### `clean.artists`

| | |
|---|---|
| **Là gì?** | Thông tin nghệ sĩ. **1,162,095 rows** — nhưng chỉ 81,776 có ít nhất 1 track trong dataset. |
| **Dùng để trả lời** | Nghệ sĩ nào có nhiều bài? Followers bao nhiêu? |
| **Không nên hiểu sai** | `artists.popularity` là popularity của **nghệ sĩ**, không phải bài hát — **không dùng làm ML input** mặc định (leakage risk). 11 artists có `followers IS NULL`. |

---

### `clean.genres`

| | |
|---|---|
| **Là gì?** | Danh sách thể loại âm nhạc. **5,366 genres.** |
| **Dùng để trả lời** | Có bao nhiêu genre? Tên genre là gì? |
| **Không nên hiểu sai** | Genre gắn vào **artist**, không gắn trực tiếp vào track. 5,366 ≠ số genre xuất hiện ở track-level (chỉ 4,672). |

---

### `clean.track_artists`

| | |
|---|---|
| **Là gì?** | Bảng liên kết track ↔ artist (many-to-many). **730,946 rows.** |
| **Dùng để trả lời** | Bài hát này có những nghệ sĩ nào? Nghệ sĩ này có những bài nào? |
| **Không nên hiểu sai** | Coverage chỉ **96.54%** — 26,224 cặp track-artist bị skip vì `artist_id` không có trong `artists.csv`. Track vẫn tồn tại, chỉ thiếu thông tin artist. |

---

### `clean.artist_genres`

| | |
|---|---|
| **Là gì?** | Bảng liên kết artist ↔ genre (many-to-many). **468,680 rows.** |
| **Dùng để trả lời** | Nghệ sĩ này thuộc genre nào? Genre này có những nghệ sĩ nào? |
| **Không nên hiểu sai** | Một artist có thể có nhiều genres. Genre join coverage = **100%** (theo `vw_data_quality_report`). |

---

## Analytics views

### `analytics.vw_tracks_overview`

| | |
|---|---|
| **Là gì?** | Snapshot đầy đủ mỗi track — projection trực tiếp từ `clean.tracks`. **586,672 rows.** |
| **Dùng để trả lời** | Một bài hát cụ thể có thuộc tính gì? Phân bố audio features? |
| **Không nên hiểu sai** | Có cột `name` và `popularity` — khác với `vw_ml_training_dataset` (không có `name`, dùng `target_popularity`). |

---

### `analytics.vw_tracks_by_decade`

| | |
|---|---|
| **Là gì?** | Tổng hợp theo thập kỷ. **12 rows** (1 row/thập kỷ). |
| **Dùng để trả lời** | Thập kỷ nào có nhiều bài nhất? Popularity trung bình theo thập kỷ? |
| **Không nên hiểu sai** | Chỉ 12 dòng không có nghĩa view rỗng — đây là data **đã aggregate**. 1990s có 108,875 tracks. |

---

### `analytics.vw_audio_trends`

| | |
|---|---|
| **Là gì?** | Audio features trung bình theo năm phát hành. **101 rows** (1921–2021). |
| **Dùng để trả lời** | Danceability/energy/acousticness thay đổi thế nào qua 100 năm? |
| **Không nên hiểu sai** | Đây là **trung bình theo năm**, không phải giá trị từng bài. Acousticness giảm từ ~0.90 (1920s) → ~0.28 (2020s) theo `EDA_INSIGHTS_REPORT.md`. |

---

### `analytics.vw_popularity_stats`

| | |
|---|---|
| **Là gì?** | Phân bố popularity theo 5 bucket. **5 rows.** |
| **Dùng để trả lời** | Bao nhiêu % bài có popularity thấp/cao? |
| **Không nên hiểu sai** | Bucket 0–20 chiếm **37.5%** (219,988 tracks) — phần lớn bài hát không nổi tiếng. |

---

### `analytics.vw_top_artists`

| | |
|---|---|
| **Là gì?** | Xếp hạng artists theo track count và avg popularity. **81,776 rows.** |
| **Dùng để trả lời** | Ai có nhiều bài nhất? Ai có popularity trung bình cao nhất? |
| **Không nên hiểu sai** | Cột `artist_popularity_dashboard_only` chỉ dùng dashboard — **KHÔNG dùng làm ML feature**. Top artist là "Die drei ???" (3,856 tracks) — audio drama Đức, không phải pop star. |

---

### `analytics.vw_genre_trends`

| | |
|---|---|
| **Là gì?** | Genre performance theo thập kỷ. **19,103 rows** (4,672 genres × các thập kỷ). |
| **Dùng để trả lời** | Genre rock có bao nhiêu bài ở 1980s? Genre nào tăng/giảm theo thời gian? |
| **Không nên hiểu sai** | Dùng CTE `DISTINCT` để tránh đếm trùng — 1 track có 3 artists cùng genre "pop" chỉ đếm **1 lần**, không phải 3. |

---

### `analytics.vw_explicit_by_decade`

| | |
|---|---|
| **Là gì?** | Tỷ lệ explicit content theo thập kỷ. **12 rows.** |
| **Dùng để trả lời** | Explicit content tăng theo thời gian không? |
| **Không nên hiểu sai** | 2020s đạt **23.1%** explicit — không có nghĩa 23% bài hát trên Spotify là explicit, chỉ trong dataset này. |

---

### `analytics.vw_duration_trends`

| | |
|---|---|
| **Là gì?** | Thống kê duration theo năm, kèm đếm outlier. **101 rows.** |
| **Dùng để trả lời** | Bài hát dài/ngắn hơn theo thời gian? Có bao nhiêu outlier? |
| **Không nên hiểu sai** | Outliers được **flag**, không bị xóa: short=26 (<10s), long=83 (>60min) theo Feature 1.5. |

---

### `analytics.vw_data_quality_report`

| | |
|---|---|
| **Là gì?** | Bảng metrics chất lượng dữ liệu. **16 rows.** |
| **Dùng để trả lời** | Dataset có warning gì? Coverage bao nhiêu %? |
| **Không nên hiểu sai** | `data_quality_status = PASS_WITH_WARNINGS` — không có lỗi cấu trúc, chỉ có warnings cần theo dõi. Một số giá trị là literal từ F1.4 log, không recompute được. |

---

### `analytics.vw_ml_training_dataset`

| | |
|---|---|
| **Là gì?** | View ML-safe cho EPIC 2. **586,672 rows**, 20 cột. |
| **Dùng để trả lời** | Tập dữ liệu để train model gồm những cột nào? |
| **Không nên hiểu sai** | `target_popularity` là **label** — không dùng làm input. Không có `name`, không có `artists.popularity`. Chưa impute NULL, chưa scale, chưa split train/test — đó là việc của EPIC 2. |

---

## Bảng tra nhanh: "Tôi muốn biết X → query đâu?"

| Câu hỏi | View / Table |
|---------|-------------|
| Dataset có bao nhiêu bài? | `vw_tracks_overview` hoặc `clean.tracks` |
| Popularity phân bố thế nào? | `vw_popularity_stats` |
| Feature nào liên quan popularity? | `vw_ml_training_dataset` (NB06) |
| Genre nào nhiều bài nhất? | `vw_genre_trends` |
| Ai nhiều bài nhất? | `vw_top_artists` |
| Dataset có warning gì? | `vw_data_quality_report` |
| Train model dùng view nào? | `vw_ml_training_dataset` |
