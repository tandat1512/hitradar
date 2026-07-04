# Data Source — HitRadar Pro

## Dataset

| Trường | Thông tin |
|--------|-----------|
| **Tên dataset** | Spotify Dataset 1921-2020, 600k+ Tracks |
| **Nguồn** | Kaggle |
| **Dataset slug** | `yamaerenay/spotify-dataset-19212020-600k-tracks` |
| **URL** | https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks |
| **Phạm vi thời gian** | 1921 – 2020 |
| **Quy mô** | 600,000+ tracks · 1,000,000+ artists |

---

## File raw thực tế (phiên bản Kaggle hiện tại)

Sau khi tải về, đặt tất cả vào thư mục `1.DỮ_LIỆU/1.1.raw/`:

| File | Kích thước | Rows | Mô tả |
|------|-----------|------|-------|
| `tracks.csv` | ~111 MB | 586,672 | Bảng fact chính — id, name, popularity, audio features (danceability, energy, valence...) |
| `artists.csv` | ~65 MB | 1,162,095 | Artist metadata — id, name, followers, genres, popularity |
| `dict_artists.json` | ~333 MB | 1M+ keys | Dict artist_id → genre list (dữ liệu bổ sung) |

### Lưu ý về sự khác biệt với tài liệu cũ

Tài liệu thiết kế ban đầu đề cập 5 file: `data.csv`, `data_by_artist.csv`, `data_by_genres.csv`,
`data_by_year.csv`, `data_w_genres.csv`. Phiên bản Kaggle hiện tại chỉ cung cấp 2 file CSV nguồn.
Ba file aggregate còn lại sẽ được **sinh ra trong pipeline EPIC 1**:

| File cần tạo | Sinh từ | Khi nào |
|-------------|---------|---------|
| `data_by_year.csv` | Aggregate `tracks.csv` theo `release_date` | Feature 1.6 Analytics Views |
| `data_by_genres.csv` | Aggregate `artists.csv` theo `genres` | Feature 1.6 Analytics Views |
| `data_w_genres.csv` | Join `tracks.csv.id_artists` → `artists.csv.genres` | Feature 1.4 Cleaning |

---

## Cách tải — Kaggle API (khuyến nghị)

### 1. Cài đặt Kaggle CLI

```bash
pip install kaggle
```

### 2. Cấu hình API key

Tải file `kaggle.json` từ https://www.kaggle.com/settings → **API** → **Create New Token**.

Đặt file vào đúng vị trí:

```bash
# Windows
%USERPROFILE%\.kaggle\kaggle.json

# macOS / Linux
~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### 3. Tải dataset

```bash
kaggle datasets download -d yamaerenay/spotify-dataset-19212020-600k-tracks \
  -p "1.DỮ_LIỆU/1.1.raw" --unzip
```

Hoặc từ thư mục gốc dự án:

```bash
cd x:\DUAN1\HitRadar_Pro
kaggle datasets download -d yamaerenay/spotify-dataset-19212020-600k-tracks -p "1.DỮ_LIỆU/1.1.raw" --unzip
```

### 4. Xác nhận

Sau khi tải xong, kiểm tra file đã có nội dung (phiên bản hiện tại gồm 2 CSV + 1 JSON):

```bash
# Windows PowerShell
Get-Item "1.DỮ_LIỆU\1.1.raw\*" | Select-Object Name, Length

# macOS / Linux
ls -lh 1.DỮ_LIỆU/1.1.raw/
```

---

## Cách tải thủ công (không dùng Kaggle API)

1. Truy cập: https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks
2. Đăng nhập tài khoản Kaggle.
3. Nhấn nút **Download** (góc trên phải trang dataset).
4. Giải nén file ZIP vừa tải.
5. Copy **2 file CSV + 1 file JSON** vào thư mục `1.DỮ_LIỆU/1.1.raw/` trong dự án:

---

## Lưu ý quan trọng

- Các file CSV và ZIP **không được commit lên Git** (đã thêm vào `.gitignore`).
- Mỗi thành viên tải dataset về máy local của mình trước khi chạy pipeline.
- Không sửa, không rename, không chuyển định dạng file raw — giữ nguyên tên Kaggle.
- File raw chỉ dùng làm input cho pipeline EPIC 1. Không dùng trực tiếp để train model.
