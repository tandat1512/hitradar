# HOW TO RUN DATA PIPELINE — HitRadar EPIC 1

> **Dự án:** HitRadar Pro | **EPIC:** EPIC 1 — Data Foundation & Data Understanding
> **Cập nhật:** Feature 1.3

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

## Bước 1 — Chạy DDL (Feature 1.2)

Tạo schema, tables, views, indexes cho database `hitradar`.

```powershell
# Set path psql
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$db   = "hitradar"
$u    = "postgres"
$dir  = "x:\DUAN1\HitRadar_Pro\2.DATABASE_SQL\2.1.tao_bang"

# Tạo database nếu chưa có
$env:PGPASSWORD = "your_password"
& $psql -U $u -d postgres -c "CREATE DATABASE hitradar;"

# Chạy 5 file DDL theo thứ tự
& $psql -U $u -d $db -f "$dir\01_create_schemas.sql"
& $psql -U $u -d $db -f "$dir\02_create_raw_tables.sql"
& $psql -U $u -d $db -f "$dir\03_create_clean_tables.sql"
& $psql -U $u -d $db -f "$dir\04_create_analytics_views.sql"
& $psql -U $u -d $db -f "$dir\05_create_constraints_indexes.sql"
```

**Kết quả mong đợi:** 0 `ERROR:` — chỉ có `NOTICE:` (bình thường khi IF NOT EXISTS).

---

## Bước 2 — Import raw data (Feature 1.3)

Import 3 raw files vào PostgreSQL raw layer.

```powershell
# Set password
$env:PGPASSWORD  = "your_password"
$env:PYTHONUTF8  = "1"

# Lần đầu (hoặc muốn reimport sạch): dùng --reset
python "x:\DUAN1\HitRadar_Pro\9.SCRIPTS\import_raw_data.py" `
    --database hitradar `
    --host localhost `
    --user postgres `
    --reset

# Lần tiếp theo (không xoá dữ liệu cũ): bỏ --reset
python "x:\DUAN1\HitRadar_Pro\9.SCRIPTS\import_raw_data.py" `
    --database hitradar --user postgres
```

**Kết quả mong đợi:**
```
raw.raw_tracks:      586,672 / 586,672  OK
raw.raw_artists:   1,162,095 / 1,162,095  OK
raw.raw_artist_json: 573,856 / 573,856  OK
Feature 1.3 import status: PASS
```

---

## Bước 3 — Validate raw import (Feature 1.3)

Kiểm tra row count, column count, ID uniqueness.

```powershell
$env:PGPASSWORD = "your_password"
$env:PYTHONUTF8 = "1"

python "x:\DUAN1\HitRadar_Pro\9.SCRIPTS\validate_raw_import.py" `
    --database hitradar --user postgres
```

**Kết quả mong đợi:** `Overall: PASS`

---

## Thứ tự chạy đầy đủ (fresh start)

```powershell
$env:PGPASSWORD = "your_password"
$env:PYTHONUTF8 = "1"
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$dir  = "x:\DUAN1\HitRadar_Pro\2.DATABASE_SQL\2.1.tao_bang"

# 1. DDL
foreach ($f in @("01","02","03","04","05") | ForEach-Object {"${_}_*.sql"}) {
    & $psql -U postgres -d hitradar -f "$dir\$f"
}

# 2. Import
python "x:\DUAN1\HitRadar_Pro\9.SCRIPTS\import_raw_data.py" --database hitradar --user postgres --reset

# 3. Validate
python "x:\DUAN1\HitRadar_Pro\9.SCRIPTS\validate_raw_import.py" --database hitradar --user postgres
```

---

## Kiểm tra nhanh bằng psql

```sql
-- Kết nối
psql -U postgres -d hitradar

-- Row counts
SELECT 'raw_tracks'      AS t, COUNT(*) FROM raw.raw_tracks
UNION ALL
SELECT 'raw_artists',           COUNT(*) FROM raw.raw_artists
UNION ALL
SELECT 'raw_artist_json',       COUNT(*) FROM raw.raw_artist_json;

-- Xem sample
SELECT id, name, popularity, release_date FROM raw.raw_tracks LIMIT 3;
SELECT id, name, genres FROM raw.raw_artists LIMIT 3;
```

---

## Files quan trọng

| File | Mô tả |
|------|-------|
| `9.SCRIPTS/import_raw_data.py` | Script import 3 raw files |
| `9.SCRIPTS/validate_raw_import.py` | Script validate sau import |
| `9.SCRIPTS/audit_raw_data.py` | Script audit raw files (Feature 1.1) |
| `9.SCRIPTS/verify_dict_artists_semantic.py` | Script xác minh dict_artists.json (Feature 1.2) |
| `2.DATABASE_SQL/2.1.tao_bang/` | 5 file DDL skeleton |
| `6.TAI_LIEU/6.1.bao_cao/IMPORT_LOG.md` | Log import lần cuối |
| `6.TAI_LIEU/6.1.bao_cao/RAW_IMPORT_VALIDATION_REPORT.md` | Validation report |
