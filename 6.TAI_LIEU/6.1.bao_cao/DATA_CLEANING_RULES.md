# DATA CLEANING RULES — HitRadar EPIC 1

> **Feature:** 1.4 — Data Cleaning & Normalization
> **Owner:** Đạt
> **Ngày:** 2026-07-07
> **Status:** Active

---

## Nguyên tắc chung

| # | Rule | Lý do |
|---|------|-------|
| G-1 | **Không drop row** nếu chưa có lý do kỹ thuật mạnh | Bảo toàn dữ liệu raw, audit trail |
| G-2 | **Không sửa raw tables** — chỉ ghi vào clean layer | Reproducibility |
| G-3 | **NULL ≠ xóa** — NULL là giá trị hợp lệ trong clean layer | FK-safe, downstream aware |

---

## 1. Missing Values

| Cột | Rule | Clean layer |
|-----|------|-------------|
| `raw_tracks.name` | Giữ NULL — không drop row | `clean.tracks.name = NULL` |
| `raw_artists.name` | Giữ NULL — không drop row | `clean.artists.name = NULL` |
| `raw_artists.followers` | Cast FLOAT → BIGINT; nếu NULL hoặc âm → NULL | `clean.artists.followers = NULL` |
| `raw_artists.popularity` | Giữ nguyên — dashboard only, không làm feature | `clean.artists.popularity` |

---

## 2. Tempo

| Điều kiện | Rule |
|-----------|------|
| `tempo = 0` | Chuyển thành `NULL` trong `clean.tracks` |
| `tempo > 0` | Giữ nguyên |

> Lý do: `tempo = 0` là sentinel value, không phải tempo thực. DDL có CHECK `tempo > 0`, nên bắt buộc đổi 0 → NULL trước khi insert.

---

## 3. Time Signature

| Điều kiện | Rule |
|-----------|------|
| `time_signature = 0` | Chuyển thành `NULL` trong `clean.tracks` |
| `time_signature IN (1,2,3,4,5)` | Giữ nguyên |

> Lý do: DDL có CHECK `time_signature BETWEEN 1 AND 5`, nên giá trị 0 phải là NULL.

---

## 4. Duration Outliers

| Điều kiện | Rule |
|-----------|------|
| `duration_ms < 10,000` (< 10s) | **Giữ lại** nhưng gắn cờ trong CLEANING_LOG.md |
| `duration_ms > 3,600,000` (> 60 phút) | **Giữ lại** nhưng gắn cờ trong CLEANING_LOG.md |
| Tất cả | `duration_min = duration_ms / 60000.0` |

> Không drop outlier ở Feature 1.4 — để Feature 1.5 (Data Quality Gates) quyết định ngưỡng.

---

## 5. Release Date Normalization

| Format raw | `release_precision` | `release_date` normalized | `release_year` | `release_month` |
|-----------|--------------------|-----------------------------|---------------|----------------|
| `YYYY-MM-DD` | `day` | `YYYY-MM-DD` (giữ nguyên) | `YYYY` | `MM` |
| `YYYY-MM` | `month` | `YYYY-MM-01` | `YYYY` | `MM` |
| `YYYY` | `year` | `YYYY-01-01` | `YYYY` | `NULL` |
| Không parse được | `unknown` | `NULL` | `NULL` | `NULL` |

> `decade = (release_year / 10) * 10` — ví dụ 1990, 2000, 2010.

---

## 6. Explicit Flag

| Raw value | Clean value |
|-----------|-------------|
| `0` | `FALSE` |
| `1` | `TRUE` |
| Khác | `FALSE` (safe default) |

---

## 7. Parse artists / id_artists

| Rule | Chi tiết |
|------|---------|
| Parser | `ast.literal_eval` — parse list-string Python |
| Fallback | Nếu parse lỗi → bỏ qua row đó trong `clean.track_artists` |
| FK check | Chỉ insert `clean.track_artists` nếu `artist_id` tồn tại trong `clean.artists` |
| `artist_order` | Index trong list (0-based) |
| `is_main_artist` | `TRUE` nếu `artist_order = 0` |

---

## 8. Parse genres

| Rule | Chi tiết |
|------|---------|
| Source | `raw.raw_artists.genres` **ONLY** |
| Parser | `ast.literal_eval` |
| Fallback | Nếu parse lỗi hoặc `[]` → skip |
| `normalized_genre_name` | `lower().strip()`, collapse multiple spaces |
| Unique | `genre_name` phải unique trong `clean.genres` |
| FK check | `clean.artist_genres` chỉ insert nếu `artist_id` tồn tại trong `clean.artists` |

---

## 9. dict_artists.json — Artist Relations

| Rule | Chi tiết |
|------|---------|
| Source | `raw.raw_artist_json.raw_values` |
| Semantic | **RELATED_ARTIST_GRAPH** — không phải genre source |
| Parser | `json.loads(raw_values)` |
| FK check | Chỉ insert cặp `(artist_id, related_artist_id)` nếu CẢ HAI tồn tại trong `clean.artists` |
| `relation_order` | Index trong list (0-based) |
| `source` | `dict_artists_json` |

> **Không dùng dict_artists.json làm genre source** — đã xác minh 100% overlap với artist IDs.

---

## 10. Thứ tự populate clean tables

```
1. clean.tracks         (no FK)
2. clean.artists        (no FK)
3. clean.genres         (no FK, SERIAL PK)
4. clean.track_artists  (FK → tracks + artists)
5. clean.artist_genres  (FK → artists + genres)
6. clean.artist_relations (FK → artists × 2)
```

---

## Tóm tắt quyết định thiết kế

| Quyết định | Lý do |
|-----------|-------|
| Không drop row có `tempo = 0`, `time_signature = 0` | NULL an toàn hơn DROP |
| Không drop duration outliers | Feature 1.5 sẽ quyết định ngưỡng |
| Genre chỉ từ `artists.csv.genres` | `dict_artists.json` đã xác minh là RELATED_ARTIST_GRAPH |
| FK filter cho `track_artists` | Tránh constraint violation, giữ data integrity |
| FK filter cho `artist_relations` | Chỉ pair artists đã biết |
