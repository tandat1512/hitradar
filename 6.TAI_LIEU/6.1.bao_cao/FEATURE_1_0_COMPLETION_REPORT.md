# FEATURE 1.0 COMPLETION REPORT

## 1. Feature

**Feature 1.0 — Data Contract & Scope Lock**

| Trường | Thông tin |
|--------|-----------|
| EPIC | EPIC 1 — Data Foundation & Data Understanding |
| Dự án | HitRadar Pro |
| Ngày hoàn thành | 2026-07-05 |
| Trạng thái | **PASS** |

---

## 2. Owner

**Đạt** — phụ trách EPIC 1

---

## 3. Completed Tasks

| Task | Mô tả | Trạng thái |
|------|-------|-----------|
| Task 1.0.1 | Xác nhận mục tiêu dữ liệu của EPIC 1 | **DONE** |
| Task 1.0.2 | Xác định input files chính thức (2 CSV + 1 JSON thực tế) | **DONE** |
| Task 1.0.3 | Xác định output bắt buộc của EPIC 1 (9 tài liệu + tables + views + export) | **DONE** |
| Task 1.0.4 | Xác định ranh giới EPIC 1 và EPIC 2 | **DONE** |
| Task 1.0.5 | Định nghĩa quy tắc không gây data leakage | **DONE** |
| Task 1.0.6 | Viết Definition of Done cho EPIC 1 | **DONE** |
| Task 1.0.7 | Ghi rõ EPIC 1 không train model, không tuning, không SHAP, không làm app | **DONE** |

---

## 4. Actual Raw Data Contract

| File | Path | Format | Kích thước | Rows | Vai trò |
|------|------|--------|-----------|------|---------|
| `tracks.csv` | `1.DỮ_LIỆU/1.1.raw/tracks.csv` | CSV | ~111 MB | 586,672 | Bảng fact track chính — audio features + popularity |
| `artists.csv` | `1.DỮ_LIỆU/1.1.raw/artists.csv` | CSV | ~65 MB | 1,162,095 | Bảng artist — followers, genres, popularity |
| `dict_artists.json` | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | JSON | ~333 MB | 573,856 keys | Dict artist_id → genre list |

---

## 5. Contract Change Note

Bản EPIC ban đầu giả định **5 CSV** làm raw input:
`data.csv`, `data_by_artist.csv`, `data_by_genres.csv`, `data_by_year.csv`, `data_w_genres.csv`

Sau khi kiểm tra Kaggle dataset phiên bản hiện tại, raw input thực tế là **2 CSV + 1 JSON**.
Contract đã được cập nhật để phản ánh dữ liệu thật, tránh tạo dữ liệu giả.

| File cũ (contract ban đầu) | Trạng thái | Xử lý |
|---------------------------|-----------|-------|
| `data.csv` | Không tồn tại | → Thay bằng `tracks.csv` |
| `data_by_artist.csv` | Không tồn tại | → Thay bằng `artists.csv` |
| `data_by_year.csv` | Không tồn tại | → Sẽ sinh từ pipeline Feature 1.6 |
| `data_by_genres.csv` | Không tồn tại | → Sẽ sinh từ pipeline Feature 1.6 |
| `data_w_genres.csv` | Không tồn tại | → Sẽ sinh từ Feature 1.4 (join) |

---

## 6. Remaining Risks

| Risk | Mức độ | Xử lý ở |
|------|--------|---------|
| Schema thực tế chưa được audit đầy đủ | Trung bình | Feature 1.1 |
| Cột chính xác và kiểu dữ liệu cần xác nhận sau khi đọc header | Thấp | Feature 1.1 |
| Missing values, duplicate, outlier range chưa kiểm tra | Trung bình | Feature 1.1 |
| Cách parse `dict_artists.json` chưa được định nghĩa chi tiết | Trung bình | Feature 1.2 / 1.4 |
| Coverage join giữa `tracks.csv.id_artists` và `artists.csv.id` chưa đo | Trung bình | Feature 1.1 / 1.5 |

---

## 7. Next Step

**Feature 1.1 — Dataset Audit & Data Dictionary**

| Việc cần làm | Output |
|-------------|--------|
| Đọc header `tracks.csv`, `artists.csv` | Danh sách cột + kiểu dữ liệu |
| Kiểm tra cấu trúc `dict_artists.json` | JSON schema |
| Tính row count, column count từng file | Bảng thống kê |
| Kiểm tra missing values từng cột | Bảng null ratio |
| Kiểm tra duplicate (id, name+artist+date) | Báo cáo duplicate |
| Kiểm tra range audio features (0–1), popularity (0–100) | Range validation |
| Kiểm tra `release_date` — các format khác nhau | Parse complexity |
| Lập `DATASET_AUDIT_REPORT.md` | Báo cáo audit đầy đủ |
| Lập `DATA_DICTIONARY.md` | Định nghĩa từng cột |

---

## 8. Files Created / Updated in Feature 1.0

| File | Hành động |
|------|----------|
| `6.TAI_LIEU/6.1.bao_cao/EPIC1_SCOPE_LOCK.md` | Viết lại đầy đủ 10 mục |
| `1.DỮ_LIỆU/DATA_SOURCE.md` | Cập nhật file thực tế + sửa ref "5 file" |
| `6.TAI_LIEU/6.1.bao_cao/DATASET_DOWNLOAD_CHECK.md` | Bổ sung Feature 1.0 closing statement |
| `6.TAI_LIEU/6.1.bao_cao/FEATURE_1_0_COMPLETION_REPORT.md` | Tạo mới (file này) |
| `1.DỮ_LIỆU/1.1.raw/tracks.csv` | Di chuyển vào đúng thư mục |
| `1.DỮ_LIỆU/1.1.raw/artists.csv` | Di chuyển vào đúng thư mục |
| `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | Di chuyển vào đúng thư mục |

---

## 9. Status

> **PASS — Feature 1.0 completed.**
>
> Data contract đã khóa. Raw input đã xác nhận. Ranh giới EPIC 1/2 rõ ràng. Leakage rules đã ghi. Sẵn sàng chuyển sang Feature 1.1.
