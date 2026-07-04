# Dataset Download Check — HitRadar Pro

**Ngày kiểm tra:** 2026-07-05 00:08 (UTC+7)

## Thông tin dataset

| Trường | Thông tin |
|--------|-----------|
| Dataset | Spotify Dataset 1921-2020, 600k+ Tracks |
| Kaggle slug | `yamaerenay/spotify-dataset-19212020-600k-tracks` |
| Thư mục raw | `1.DỮ_LIỆU/1.1.raw/` |
| Phương thức tải | Thủ công từ Kaggle |

## Kiểm tra file raw

| File | Kích thước | Rows | Trạng thái | Ghi chú |
|------|-----------|------|-----------|---------|
| `tracks.csv` | 111,366,271 bytes | 586,672 | **OK** | Bảng fact chính — 600k+ tracks, audio features + popularity |
| `artists.csv` | 64,893,749 bytes | 1,162,095 | **OK** | Artist metadata — followers, genres, popularity (1M+ artists) |
| `dict_artists.json` | 332,576,243 bytes | 573,856 keys | **OK** | Dict artist_id → genre list (bổ sung) |

## Ghi chú về cấu trúc dataset

Phiên bản Kaggle hiện tại (2024-2025) của dataset này có **2 file CSV nguồn chính**
thay vì 5 file như tài liệu cũ đề cập. Mapping như sau:

| File Kaggle thực tế | Tương đương tài liệu cũ | Trạng thái |
|--------------------|-----------------------|-----------|
| `tracks.csv` | `data.csv` | **Có sẵn** |
| `artists.csv` | `data_by_artist.csv` | **Có sẵn** |
| `artists.csv` (aggregate genres) | `data_w_genres.csv` | **Sẽ derive từ `artists.csv`** |
| Aggregate từ `tracks.csv` theo year | `data_by_year.csv` | **Sẽ tạo trong pipeline** |
| Aggregate từ `artists.csv` theo genres | `data_by_genres.csv` | **Sẽ tạo trong pipeline** |

Ba file aggregate sẽ được tạo tự động trong **Feature 1.4 (Data Cleaning)** và
**Feature 1.6 (Analytics Views)** của EPIC 1.

## Kết luận: **PASS**

Tất cả file raw có dữ liệu thật. Sẵn sàng cho Feature 1.1 — Dataset Audit.

---

## Feature 1.0 Closing Statement

**Feature 1.0 raw data acquisition is complete based on current Kaggle dataset structure.**

Raw input contract đã được cập nhật từ "5 CSV cũ" sang "2 CSV + 1 JSON thực tế".
Ba file aggregate (`data_by_year`, `data_by_genres`, `data_w_genres`) sẽ được sinh trong pipeline EPIC 1.