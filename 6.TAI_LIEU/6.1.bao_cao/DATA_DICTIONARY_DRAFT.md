# DATA DICTIONARY DRAFT — FEATURE 1.1

> **Trạng thái:** Draft — sẽ được xác nhận và mở rộng sau Feature 1.4 (Cleaning)
> **Người tạo:** Đạt · **Ngày:** 2026-07-05
> **Nguồn:** Audit thực tế từ `tracks.csv`, `artists.csv`, `dict_artists.json`

---

## Quy ước phân loại

**Role:**
`ID` · `target` · `audio_feature` · `time` · `artist_metadata` · `genre_metadata` · `technical_metadata` · `dashboard_only` · `ML_candidate` · `unknown_need_review`

**ML Usage:**
`yes` · `no` · `target_only` · `caution` · `dashboard_only` · `need_review`

---

## tracks.csv — 20 columns · 586,672 rows

| Source | Column | Data Type | Meaning | Role | ML Usage | Risk Note |
|--------|--------|-----------|---------|------|----------|-----------|
| tracks.csv | `id` | object | Spotify track ID — mã định danh duy nhất của bài hát | ID | no | Dùng làm primary key, không encode làm feature |
| tracks.csv | `name` | object | Tên bài hát | artist_metadata | no | Text tự do, 71 missing (0.01%), không dùng làm numeric feature |
| tracks.csv | `popularity` | int64 | Độ phổ biến bài hát (0–100) do Spotify tính theo lượt nghe gần đây | target | target_only | **Target chính của mô hình.** Không được dùng làm input feature. Phân bố lệch — mean 27.57, median 27. |
| tracks.csv | `duration_ms` | int64 | Thời lượng bài hát tính bằng milliseconds | technical_metadata | yes | Cần tạo `duration_min`. Max = 5,621,218 ms (~93 phút) — cần kiểm tra outlier ở Feature 1.4. |
| tracks.csv | `explicit` | int64 | Nội dung explicit: 1 = có, 0 = không | technical_metadata | yes | Boolean, encode sẵn. Chỉ 4.4% bài là explicit. |
| tracks.csv | `artists` | object | Tên nghệ sĩ — dạng list-string Python: `['Artist A', 'Artist B']` | artist_metadata | caution | **Cần parse.** Không dùng trực tiếp. Phải tách thành bảng track_artists ở Feature 1.4. |
| tracks.csv | `id_artists` | object | Spotify artist ID tương ứng — dạng list-string: `['id1', 'id2']` | ID | no | Dùng để join với `artists.csv.id`. Cần explode ở Feature 1.4. |
| tracks.csv | `release_date` | object | Ngày/năm phát hành — 2 format: `YYYY-MM-DD` hoặc `YYYY` | time | caution | **Cần parse.** Tạo `release_year`, `release_month`, `decade` ở Feature 1.4. 19,700 unique values. |
| tracks.csv | `danceability` | float64 | Mức độ phù hợp để nhảy (0–1): nhịp, beat strength, regularity | audio_feature | yes | Không có missing. Range OK [0, 0.991]. |
| tracks.csv | `energy` | float64 | Cường độ và hoạt động âm nhạc (0–1): nhanh, mạnh, ồn | audio_feature | yes | Không có missing. Range OK [0, 1]. |
| tracks.csv | `key` | int64 | Tông bài hát: 0–11 (C, C#, D… B theo pitch class notation) | audio_feature | yes | Categorical — cần one-hot hoặc encode ở EPIC 2. 12 unique values. |
| tracks.csv | `loudness` | float64 | Độ lớn âm thanh trung bình (dB): thường từ -60 đến 0 dB | audio_feature | yes | Range [-60.0, 5.376]. Có thể chuẩn hóa. |
| tracks.csv | `mode` | int64 | Điệu thức: 1 = major, 0 = minor | audio_feature | yes | Binary. 65.9% bài là major. |
| tracks.csv | `speechiness` | float64 | Mức độ lời nói (0–1): > 0.66 là spoken word, 0.33–0.66 pha lời | audio_feature | yes | Phân bố lệch phải mạnh — median = 0.044, mean = 0.105. |
| tracks.csv | `acousticness` | float64 | Xác suất bài là acoustic (0–1) | audio_feature | yes | Phân bố tương đối đồng đều. Mean = 0.450. |
| tracks.csv | `instrumentalness` | float64 | Xác suất không có vocal (0–1): gần 1 là thuần instrumental | audio_feature | yes | **Phân bố cực lệch:** median ≈ 0.000024. Đa số bài có vocal. |
| tracks.csv | `liveness` | float64 | Xác suất bài được thu live (0–1): > 0.8 gợi ý live recording | audio_feature | yes | Mean = 0.214, median = 0.139. |
| tracks.csv | `valence` | float64 | Cảm xúc tích cực (0–1): cao = vui/tươi, thấp = buồn/tối | audio_feature | yes | Phân bố gần đều. Mean = 0.552. |
| tracks.csv | `tempo` | float64 | Nhịp độ bài hát (BPM — beats per minute) | audio_feature | yes | **WARNING:** 328 giá trị = 0.0 (0.056%). Cần xử lý ở Feature 1.4. Mean = 118.5 BPM. |
| tracks.csv | `time_signature` | int64 | Số beat mỗi ô nhịp: thường 3–5 (4/4 là phổ biến nhất) | technical_metadata | yes | 5 unique values [0–5]. Categorical — có thể encode. |

---

## artists.csv — 5 columns · 1,162,095 rows

| Source | Column | Data Type | Meaning | Role | ML Usage | Risk Note |
|--------|--------|-----------|---------|------|----------|-----------|
| artists.csv | `id` | object | Spotify artist ID — mã định danh duy nhất của nghệ sĩ | ID | no | Primary key. Dùng để join với `tracks.csv.id_artists`. Unique 100%. |
| artists.csv | `followers` | float64 | Số lượng người theo dõi nghệ sĩ trên Spotify | artist_metadata | caution | 11 missing (0.001%). Phân bố cực lệch phải — max = 78.9M, median = 57. Nếu dùng làm feature cần log-transform. **Rủi ro leakage** nếu join vào training set. |
| artists.csv | `genres` | object | Danh sách genre của nghệ sĩ — list-string Python: `['pop', 'rock']` | genre_metadata | caution | **Cần parse.** Nhiều giá trị là `[]`. 49,155 unique combinations. Tách thành bảng artist_genres ở Feature 1.4. |
| artists.csv | `name` | object | Tên nghệ sĩ | artist_metadata | no | 3 missing (0.0003%). Text, không dùng làm numeric feature. |
| artists.csv | `popularity` | int64 | Độ phổ biến của nghệ sĩ (0–100) | artist_metadata | caution | **Leakage risk cao.** Không được dùng trực tiếp làm ML feature mà chưa có rule leakage-safe từ EPIC 2. Chỉ dùng cho EDA/dashboard. Mean = 8.80, median = 2 — phân bố lệch mạnh. |

---

## dict_artists.json — mapping file

| Source | Key/Field | Data Type | Meaning | Role | ML Usage | Risk Note |
|--------|-----------|-----------|---------|------|----------|-----------|
| dict_artists.json | key | str | Spotify artist ID — giống `artists.csv.id` | ID | no | 573,856 keys. Dùng để map artist → genre. |
| dict_artists.json | value | list[str] | Danh sách genre của artist | genre_metadata | caution | **50.82% là list rỗng []** — join sẽ cho nhiều NULL. 1,079,349 unique genre strings (cần làm sạch). Nguồn bổ sung cho `artists.csv.genres`. |

---

## Feature Engineering Candidates (được tạo ở Feature 1.4 / EPIC 2)

| Column mới | Tính từ | Mô tả | Role | ML Usage |
|-----------|---------|-------|------|----------|
| `release_year` | `release_date` | Năm phát hành (integer) | time | yes |
| `release_month` | `release_date` | Tháng phát hành (1-12, nếu đủ dữ liệu) | time | caution |
| `decade` | `release_date` / `release_year` | Thập kỷ phát hành: 1920, 1930… 2020 | time | yes |
| `duration_min` | `duration_ms` | Thời lượng tính bằng phút (float) | technical_metadata | yes |
| `main_artist_id` | `id_artists` (explode) | ID của nghệ sĩ chính (đầu tiên trong list) | ID | no |
| `main_artist_name` | `artists` (explode) | Tên nghệ sĩ chính | artist_metadata | no |
| `genre_list` | `artists.csv.genres` hoặc `dict_artists.json` | Danh sách genre sau khi parse | genre_metadata | caution |
| `n_artists` | `id_artists` | Số nghệ sĩ trong một track | ML_candidate | yes |
| `is_explicit` | `explicit` | Boolean rõ ràng hơn | technical_metadata | yes |

---

## Phân loại nhanh theo vai trò ML

| ML Usage | Columns |
|----------|---------|
| **target_only** | `tracks.popularity` |
| **yes** (ML candidate) | `duration_ms`, `explicit`, `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, `time_signature` |
| **caution** | `release_date` (cần parse), `artists` (cần parse), `id_artists` (chỉ dùng để join), `artists.followers` (leakage risk), `artists.genres` (cần parse), `artists.popularity` (leakage risk), `dict_artists.json value` |
| **no** | `id` (tracks), `name` (tracks), `id` (artists), `name` (artists), tất cả raw ID fields |
| **dashboard_only** | `artists.popularity` (cho đến khi EPIC 2 xác nhận leakage-safe rule) |
