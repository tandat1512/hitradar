# HOW TO RUN DATA PIPELINE — HitRadar EPIC 1

> **Dự án:** HitRadar Pro | **EPIC:** EPIC 1 — Data Foundation & Data Understanding
> **Cập nhật:** Feature 1.3 hotfix (reproducible pipeline)

---

## Yêu cầu hệ thống

| Thành phần | Phiên bản | Ghi chú |
|-----------|----------|---------|
| PostgreSQL | 18.x | Đang chạy trên localhost:5432 |
| Python | 3.10+ | Có trong PATH |
| psycopg2-binary | 2.9+ | `pip install psycopg2-binary` |
| pandas | 2.0+ | `pip install pandas` |

---

## Bước 0 — Cài đặt dependencies

```powershell
pip install psycopg2-binary pandas
```

---

## Bước 1 — Khai báo biến dự án

Thay `X:\DUAN1\HitRadar_Pro` bằng đường dẫn thực tế trên máy bạn.

```powershell
$project = "X:\DUAN1\HitRadar_Pro"
$psql    = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$db      = "hitradar"
$u       = "postgres"
$ddl     = "$project\2.DATABASE_SQL\2.1.tao_bang"

# Đặt password — không hardcode vào script
$env:PGPASSWORD = "your_password"
$env:PYTHONUTF8 = "1"
```

> **Lưu ý bảo mật:** Không commit `$env:PGPASSWORD` vào git.
> Dùng `.pgpass` (Linux/Mac) hoặc Windows Credential Manager cho môi trường production.

---

## Bước 2 — Tạo database (nếu chưa có)

```powershell
& $psql -v ON_ERROR_STOP=1 -U $u -d postgres -c "CREATE DATABASE hitradar;"
```

---

## Bước 3 — Chạy DDL (Feature 1.2)

Tạo schemas, tables, views, indexes theo đúng thứ tự. **Bắt buộc chạy từ 01 đến 05.**

```powershell
$ddlFiles = @(
    "01_create_schemas.sql",
    "02_create_raw_tables.sql",
    "03_create_clean_tables.sql",
    "04_create_analytics_views.sql",
    "05_create_constraints_indexes.sql"
)

foreach ($f in $ddlFiles) {
    Write-Host "--- $f ---"
    & $psql -v ON_ERROR_STOP=1 -U $u -d $db -f "$ddl\$f"
    if ($LASTEXITCODE -ne 0) { Write-Error "FAILED: $f"; break }
}
```

**Kết quả mong đợi:** Không có dòng `ERROR:` — chỉ có `NOTICE:` (bình thường khi bảng đã tồn tại).

> `-v ON_ERROR_STOP=1` đảm bảo psql dừng ngay khi gặp lỗi SQL, không bỏ qua lỗi.

---

## Bước 4 — Import raw data (Feature 1.3)

### Lần đầu hoặc muốn reimport sạch — dùng `--reset`

```powershell
python "$project\9.SCRIPTS\import_raw_data.py" `
    --base-dir $project `
    --database $db `
    --user     $u `
    --reset
```

### Chạy thêm (không xóa dữ liệu cũ) — bỏ `--reset`

```powershell
python "$project\9.SCRIPTS\import_raw_data.py" `
    --base-dir $project `
    --database $db `
    --user     $u
```

**Kết quả mong đợi (Feature 1.3 baseline):**

```
raw.raw_tracks:        586,672 / 586,672  OK
raw.raw_artists:     1,162,095 / 1,162,095  OK
raw.raw_artist_json:   573,856 / 573,856  OK
Feature 1.3 import status: PASS
```

> Nếu `release_precision` không tồn tại trong `clean.tracks` — script sẽ **FAIL** ngay bước prerequisite.
> Đây là cơ chế kiểm tra DDL Feature 1.2 đã chạy đúng.

---

## Bước 5 — Validate raw import (Feature 1.3)

```powershell
python "$project\9.SCRIPTS\validate_raw_import.py" `
    --base-dir $project `
    --database $db `
    --user     $u
```

**Kết quả mong đợi:** `Overall: PASS`

---

## Chạy toàn bộ pipeline (fresh start)

```powershell
# 0. Biến
$project = "X:\DUAN1\HitRadar_Pro"
$psql    = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$db      = "hitradar"; $u = "postgres"
$ddl     = "$project\2.DATABASE_SQL\2.1.tao_bang"
$env:PGPASSWORD = "your_password"; $env:PYTHONUTF8 = "1"

# 1. DDL
$ddlFiles = @(
    "01_create_schemas.sql","02_create_raw_tables.sql",
    "03_create_clean_tables.sql","04_create_analytics_views.sql",
    "05_create_constraints_indexes.sql"
)
foreach ($f in $ddlFiles) {
    & $psql -v ON_ERROR_STOP=1 -U $u -d $db -f "$ddl\$f"
    if ($LASTEXITCODE -ne 0) { Write-Error "DDL failed: $f"; break }
}

# 2. Import
python "$project\9.SCRIPTS\import_raw_data.py" `
    --base-dir $project --database $db --user $u --reset

# 3. Validate
python "$project\9.SCRIPTS\validate_raw_import.py" `
    --base-dir $project --database $db --user $u

# 4. Clean (Feature 1.4)
python "$project\9.SCRIPTS\clean_raw_to_clean.py" `
    --base-dir $project --database $db --user $u --reset-clean

# 5. Validate clean
python "$project\9.SCRIPTS\validate_clean_tables.py" `
    --base-dir $project --database $db --user $u
```

---

## Feature 1.4 — Data Cleaning & Normalization

### Bước 6 — (Tùy chọn) Mở notebook exploration

```powershell
jupyter notebook "$project\3.NOTEBOOKS\3.3.lam_sach_python\01_feature_1_4_cleaning_exploration.ipynb"
```

### Bước 7 — Chạy cleaning script

```powershell
$env:PGPASSWORD = "your_password"
$project = "X:\DUAN1\HitRadar_Pro"

python "$project\9.SCRIPTS\clean_raw_to_clean.py" `
    --base-dir $project --database hitradar --user postgres --reset-clean
```

**Kết quả mong đợi:**
```
clean.tracks:           586,672
clean.artists:        1,162,095
clean.genres:             5,366
clean.track_artists:    730,946
clean.artist_genres:    468,680
clean.artist_relations: 8,864,471
Feature 1.4 cleaning status: PASS
```

### Bước 8 — Chạy validate clean

```powershell
python "$project\9.SCRIPTS\validate_clean_tables.py" `
    --base-dir $project --database hitradar --user postgres
```

**Kết quả mong đợi:** `Overall: PASS`

### Bước 9 — (Tùy chọn) Mở notebook validation

```powershell
jupyter notebook "$project\3.NOTEBOOKS\3.3.lam_sach_python\02_feature_1_4_clean_validation.ipynb"
```

### Bước 10 — Kiểm tra reports

```powershell
# Reports sinh tự động sau khi chạy scripts:
# - $project\6.TAI_LIEU\6.1.bao_cao\CLEANING_LOG.md
# - $project\6.TAI_LIEU\6.1.bao_cao\CLEAN_TABLE_VALIDATION_REPORT.md
```

### Reset clean tables nếu cần chạy lại

```powershell
$psql    = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$project = "X:\DUAN1\HitRadar_Pro"
& $psql -v ON_ERROR_STOP=1 -U postgres -d hitradar `
    -f "$project\2.DATABASE_SQL\2.3.lam_sach\01_reset_clean_tables.sql"
```

---

## Feature 1.3 clean verification

Lệnh xác minh lại pipeline sau khi hotfix:

```powershell
$env:PGPASSWORD = "your_password"
$project = "X:\DUAN1\HitRadar_Pro"

python "$project\9.SCRIPTS\import_raw_data.py" `
    --base-dir $project --database hitradar --user postgres --reset

python "$project\9.SCRIPTS\validate_raw_import.py" `
    --base-dir $project --database hitradar --user postgres
```

**Expected baseline:**

| Table | Rows |
|-------|------|
| `raw.raw_tracks` | 586,672 |
| `raw.raw_artists` | 1,162,095 |
| `raw.raw_artist_json` | 573,856 |
| **Overall** | **PASS** |

---

## Kiểm tra nhanh bằng psql

```sql
-- Kết nối
psql -U postgres -d hitradar

-- Row counts
SELECT 'raw_tracks'        AS t, COUNT(*) FROM raw.raw_tracks
UNION ALL
SELECT 'raw_artists',              COUNT(*) FROM raw.raw_artists
UNION ALL
SELECT 'raw_artist_json',          COUNT(*) FROM raw.raw_artist_json;

-- Xem sample
SELECT id, name, popularity, release_date FROM raw.raw_tracks LIMIT 3;
SELECT id, name, genres FROM raw.raw_artists LIMIT 3;
```

---

## Evidence logs

Terminal output nên được lưu lại để audit trail:

```powershell
# Import log
python "$project\9.SCRIPTS\import_raw_data.py" ... | Tee-Object `
    -FilePath "$project\6.TAI_LIEU\6.1.bao_cao\evidence\feature_1_3_import_terminal_log.txt"

# Validation log
python "$project\9.SCRIPTS\validate_raw_import.py" ... | Tee-Object `
    -FilePath "$project\6.TAI_LIEU\6.1.bao_cao\evidence\feature_1_3_validation_terminal_log.txt"
```

Các file này được gitignore (chứa output thực tế có thể lớn).

---

## User / Database conventions

| Mục | Giá trị mặc định | Ghi chú |
|-----|-----------------|---------|
| PostgreSQL user | `postgres` | Superuser local |
| Database | `hitradar` | Tạo riêng cho dự án |
| Application user (future) | `hitradar_app` | Chỉ có quyền SELECT/INSERT trên clean + analytics |
| Password | Không hardcode | Dùng `PGPASSWORD` hoặc `.pgpass` |

---

---

## Feature 1.5 — Data Quality Gates

Chạy 12 quality gates trên clean layer. Read-only — không sửa database.

```powershell
# Run all 12 gates
$env:PGPASSWORD = "your_password"
python "$project\9.SCRIPTS\run_data_quality_gates.py" `
    --base-dir $project --database hitradar --user postgres
```

**Kết quả mong đợi (baseline):**

| Gate | Kết quả |
|------|---------|
| G01 Null Ratio | PASS |
| G02 Duplicates | PASS |
| G03 Audio Range | PASS |
| G04 Popularity Range | PASS |
| G05 Duration | WARNING (short=26, long=83) |
| G06 Tempo/Loudness | WARNING (loudness>0 = 219) |
| G07 Release Date | PASS |
| G08 Artist Coverage | PASS (96.54%) |
| G09 Genre Coverage | PASS (100.00%) |
| G10 Row Counts | PASS |
| G11 FK Orphans | PASS |
| G12 ML-safe Notes | PASS |
| **Overall** | **PASS_WITH_WARNINGS** |

**Quyết định:**
- `PASS` hoặc `PASS_WITH_WARNINGS` → **Được chuyển Feature 1.6**.
- `FAIL` → **Không được chuyển**. Quay lại Feature 1.4 hoặc mở Feature 1.5 follow-up.

**Reports:**
- `6.TAI_LIEU/6.1.bao_cao/DATA_QUALITY_RULES.md` — Gate definitions
- `6.TAI_LIEU/6.1.bao_cao/DATA_QUALITY_REPORT.md` — Auto-generated report
- `2.DATABASE_SQL/2.3.lam_sach/03_data_quality_gates.sql` — Manual SQL checks

---

## Files quan trọng

| File | Mô tả |
|------|-------|
| `9.SCRIPTS/import_raw_data.py` | Script import 3 raw files |
| `9.SCRIPTS/validate_raw_import.py` | Script validate sau import |
| `9.SCRIPTS/audit_raw_data.py` | Script audit raw files (Feature 1.1) |
| `9.SCRIPTS/verify_dict_artists_semantic.py` | Script xác minh dict_artists.json (Feature 1.2) |
| `9.SCRIPTS/clean_raw_to_clean.py` | Script cleaning Feature 1.4 |
| `9.SCRIPTS/validate_clean_tables.py` | Script validate clean layer (extended) |
| `9.SCRIPTS/run_data_quality_gates.py` | Script data quality gates Feature 1.5 |
| `2.DATABASE_SQL/2.1.tao_bang/` | 5 file DDL (chạy theo thứ tự 01→05) |
| `2.DATABASE_SQL/2.3.lam_sach/` | SQL cleaning + quality checks |
| `6.TAI_LIEU/6.1.bao_cao/IMPORT_LOG.md` | Log import lần cuối |
| `6.TAI_LIEU/6.1.bao_cao/RAW_IMPORT_VALIDATION_REPORT.md` | Validation report raw layer |
| `6.TAI_LIEU/6.1.bao_cao/CLEAN_TABLE_VALIDATION_REPORT.md` | Validation report clean layer |
| `6.TAI_LIEU/6.1.bao_cao/DATA_QUALITY_REPORT.md` | Quality gate report |
| `6.TAI_LIEU/6.1.bao_cao/evidence/` | Terminal logs (audit trail) |
