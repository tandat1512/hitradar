# HOW TO RUN DATA PIPELINE — HitRadar EPIC 1

> **Dự án:** HitRadar Pro | **EPIC:** EPIC 1 — Data Foundation & Data Understanding
> **Cập nhật:** EPIC 1 pipeline through Feature 1.9 — Documentation & Epic Review

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

---

## Feature 1.6 — Analytics Views & Indexes

Tạo 10 analytics views và indexes từ clean layer.

```powershell
$env:PGPASSWORD = "your_password"
$views = "$project\2.DATABASE_SQL\2.4.views"
$idx   = "$project\2.DATABASE_SQL\2.5.indexes"

# 1. Tạo views (DROP + CREATE OR REPLACE — idempotent)
& $psql -v ON_ERROR_STOP=1 -U $u -d $db -f "$views\01_create_analytics_views.sql"

# 2. Tạo indexes (CREATE IF NOT EXISTS — idempotent)
& $psql -v ON_ERROR_STOP=1 -U $u -d $db -f "$idx\01_create_indexes.sql"

# 3. Validate views
python "$project\9.SCRIPTS\validate_analytics_views.py" `
    --base-dir $project --database $db --user $u
```

**Kết quả mong đợi:**

| Check | Kết quả |
|-------|---------|
| 10 views exist | PASS |
| vw_tracks_overview count | 586,672 |
| vw_ml_training_dataset count | 586,672 |
| vw_top_artists count | 81,776 |
| vw_genre_trends count | 19,103 |
| ML-safe audit | PASS (no leakage) |
| Genre dedup CTE | PASS |
| Overall | PASS |

**Quyết định:**
- `PASS` hoặc `PASS_WITH_WARNINGS` → **Được chuyển Feature 1.7**.
- `FAIL` → Kiểm tra views bị lỗi, chạy lại SQL.

**Optional:** Chạy EXPLAIN ANALYZE thủ công:
```powershell
& $psql -U $u -d $db -f "$views\02_explain_analyze_queries.sql"
```

---

## Feature 1.7 — EDA & Data Understanding Notebooks

Chạy 6 EDA notebooks theo thứ tự để phân tích dữ liệu từ analytics views.

```powershell
$env:PGPASSWORD = "your_password"

# Mở Jupyter Notebook trong thư mục EDA
jupyter notebook "$project\3.NOTEBOOKS\3.4.eda"
```

**Thứ tự chạy notebooks:**

| # | File | Mục tiêu |
|---|------|---------|
| 01 | `01_dataset_overview.ipynb` | Tổng quan dataset, data quality check |
| 02 | `02_popularity_analysis.ipynb` | Phân bố popularity (label ML) |
| 03 | `03_audio_features_distribution.ipynb` | Phân bố và trend 7 audio features |
| 04 | `04_time_decade_trends.ipynb` | Explicit, duration, track count theo thập kỷ |
| 05 | `05_artist_genre_analysis.ipynb` | Top artists, genres, coverage warning |
| 06 | `06_correlation_outlier_analysis.ipynb` | Correlation với target, outlier analysis |

**Lưu ý khi chạy:**
- Đặt `PGPASSWORD` trước khi mở Jupyter.
- Chạy từng cell theo thứ tự từ trên xuống dưới (Run All hoặc Shift+Enter từng cell).
- Mỗi notebook tự đóng connection ở cell cuối.

**Kết quả mong đợi:**

| Check | Kết quả |
|-------|---------|
| Kết nối DB thành công | 6/6 notebooks |
| Biểu đồ render | ✅ |
| Không lỗi SQL | ✅ |
| target_popularity đánh dấu là label | ✅ |
| Insight có bằng chứng | ✅ |
| Overall | PASS_WITH_WARNINGS |

**Reports tạo ra:**
```
6.TAI_LIEU/6.1.bao_cao/
├── EDA_INSIGHTS_REPORT.md
├── EDA_NOTEBOOK_VALIDATION_REPORT.md
└── FEATURE_1_7_COMPLETION_REPORT.md
```

**Quyết định:**
- Notebooks chạy pass + có insight → **Được chuyển Feature 1.8 — ML-safe Handoff**.
- Notebook lỗi SQL → Kiểm tra DB connection, đảm bảo Feature 1.6 đã chạy.

---

## Feature 1.8 — ML-Safe Dataset Handoff

Tạo view ML-ready, export CSV/Parquet, validate và bàn giao sang EPIC 2.

```powershell
$env:PGPASSWORD = "your_password"
$handoff = "$project\2.DATABASE_SQL\2.6.ml_handoff"

# 1. Tạo view analytics.vw_ml_ready_dataset
& $psql -v ON_ERROR_STOP=1 -U $u -d $db -f "$handoff\01_create_ml_ready_dataset.sql"

# 2. Export CSV + Parquet
python "$project\9.SCRIPTS\export_ml_ready_dataset.py" `
    --base-dir $project --database $db --user $u

# 3. Validate (read-only)
python "$project\9.SCRIPTS\validate_ml_ready_dataset.py" `
    --base-dir $project --database $db --user $u
```

**Kết quả mong đợi:**

| Check | Kết quả |
|-------|---------|
| `analytics.vw_ml_ready_dataset` tồn tại | ✅ |
| Row count = 586,672 | ✅ |
| 20 columns (no leakage) | ✅ |
| CSV export tồn tại | ✅ |
| Parquet export | ✅ hoặc WARNING nếu thiếu pyarrow |
| Overall validation | PASS hoặc PASS_WITH_WARNINGS |

**Outputs tạo ra:**
```
2.DATABASE_SQL/2.6.ml_handoff/01_create_ml_ready_dataset.sql
5.DATA/processed/ml_ready_dataset.csv
5.DATA/processed/ml_ready_dataset.parquet   (nếu có dependency)
6.TAI_LIEU/6.1.bao_cao/
├── feature_dictionary.md
├── ml_excluded_columns.md
├── data_leakage_risks.md
├── popularity_limitations.md
├── handoff_to_epic2.md
├── ML_READY_DATASET_VALIDATION_REPORT.md
└── FEATURE_1_8_COMPLETION_REPORT.md
```

**Quyết định:**
- Validation PASS hoặc PASS_WITH_WARNINGS + CSV OK + không leakage → **Đóng Feature 1.8, chuyển Feature 1.9**.
- FAIL (thiếu view, row count sai, leakage columns, thiếu CSV) → Kiểm tra Feature 1.6/1.7 đã chạy, chạy lại pipeline.

---

## Feature 1.9 — Documentation & Epic Review

**Không chạy SQL. Không sửa DB. Chỉ review và hoàn thiện documentation.**

### Docs cần kiểm tra

| # | File | Mục tiêu |
|---|------|---------|
| 1 | `DATA_DICTIONARY.md` | Official data dictionary EPIC 1 |
| 2 | `DATABASE_SCHEMA.md` | Schema 3-layer + ML handoff |
| 3 | `DATA_CLEANING_RULES.md` | Final cleaning rules |
| 4 | `DATA_QUALITY_REPORT.md` | Final quality summary |
| 5 | `EDA_FINDINGS.md` | EDA insights tổng hợp |
| 6 | `HOW_TO_RUN_DATA_PIPELINE.md` | Pipeline guide đầy đủ F1.2–F1.9 |
| 7 | `EPIC1_DEFINITION_OF_DONE_REVIEW.md` | DoD checklist F1.0–F1.9 |
| 8 | `EPIC1_SPRINT_REVIEW_DEMO.md` | Demo script 5 phút |
| 9 | `FEATURE_1_9_COMPLETION_REPORT.md` | Feature 1.9 completion |

### Quy trình review

```powershell
# Không cần PGPASSWORD — chỉ đọc docs
$docs = "$project\6.TAI_LIEU\6.1.bao_cao"

# Kiểm tra từng file tồn tại
@(
    "DATA_DICTIONARY.md",
    "DATABASE_SCHEMA.md",
    "DATA_CLEANING_RULES.md",
    "DATA_QUALITY_REPORT.md",
    "EDA_FINDINGS.md",
    "EPIC1_DEFINITION_OF_DONE_REVIEW.md",
    "EPIC1_SPRINT_REVIEW_DEMO.md",
    "FEATURE_1_9_COMPLETION_REPORT.md"
) | ForEach-Object {
    $path = Join-Path $docs $_
    if (Test-Path $path) { Write-Host "OK: $_" } else { Write-Host "MISSING: $_" }
}
```

**Kết quả mong đợi:**

| Check | Kết quả |
|-------|---------|
| Tất cả 9 docs F1.9 tồn tại | ✅ |
| DoD review: features 1.0–1.9 có evidence | ✅ |
| Không có FAIL gate / FAIL validation | ✅ |
| EPIC 1 decision | PASS_WITH_WARNINGS |
| Sprint Review demo script sẵn sàng | ✅ |

**Quyết định:**
- Docs đủ + DoD PASS_WITH_WARNINGS → **Đóng EPIC 1, Sprint Review, chuyển EPIC 2**.
- Thiếu evidence file quan trọng → đánh dấu BLOCKED trong DoD review.

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
| `9.SCRIPTS/validate_analytics_views.py` | Script validate analytics views Feature 1.6 |
| `9.SCRIPTS/export_ml_ready_dataset.py` | Script export ML-ready dataset Feature 1.8 |
| `9.SCRIPTS/validate_ml_ready_dataset.py` | Script validate ML-ready dataset Feature 1.8 |
| `2.DATABASE_SQL/2.6.ml_handoff/` | SQL ML handoff view Feature 1.8 |
| `2.DATABASE_SQL/2.1.tao_bang/` | 5 file DDL (chạy theo thứ tự 01→05) |
| `2.DATABASE_SQL/2.3.lam_sach/` | SQL cleaning + quality checks |
| `2.DATABASE_SQL/2.4.views/` | SQL analytics views |
| `2.DATABASE_SQL/2.5.indexes/` | SQL indexes |
| `6.TAI_LIEU/6.1.bao_cao/IMPORT_LOG.md` | Log import lần cuối |
| `6.TAI_LIEU/6.1.bao_cao/RAW_IMPORT_VALIDATION_REPORT.md` | Validation report raw layer |
| `6.TAI_LIEU/6.1.bao_cao/CLEAN_TABLE_VALIDATION_REPORT.md` | Validation report clean layer |
| `6.TAI_LIEU/6.1.bao_cao/DATA_QUALITY_REPORT.md` | Quality gate report |
| `6.TAI_LIEU/6.1.bao_cao/ANALYTICS_VIEW_VALIDATION_REPORT.md` | Analytics view validation |
| `3.NOTEBOOKS/3.4.eda/01_dataset_overview.ipynb` | EDA Notebook 01 — Dataset Overview |
| `3.NOTEBOOKS/3.4.eda/02_popularity_analysis.ipynb` | EDA Notebook 02 — Popularity Analysis |
| `3.NOTEBOOKS/3.4.eda/03_audio_features_distribution.ipynb` | EDA Notebook 03 — Audio Features |
| `3.NOTEBOOKS/3.4.eda/04_time_decade_trends.ipynb` | EDA Notebook 04 — Time & Decade Trends |
| `3.NOTEBOOKS/3.4.eda/05_artist_genre_analysis.ipynb` | EDA Notebook 05 — Artist & Genre |
| `3.NOTEBOOKS/3.4.eda/06_correlation_outlier_analysis.ipynb` | EDA Notebook 06 — Correlation & Outlier |
| `6.TAI_LIEU/6.1.bao_cao/EDA_INSIGHTS_REPORT.md` | EDA insights summary (Feature 1.7) |
| `6.TAI_LIEU/6.1.bao_cao/EDA_NOTEBOOK_VALIDATION_REPORT.md` | Notebook validation report (Feature 1.7) |
| `6.TAI_LIEU/6.1.bao_cao/FEATURE_1_7_COMPLETION_REPORT.md` | Feature 1.7 completion report |
| `6.TAI_LIEU/6.1.bao_cao/feature_dictionary.md` | ML feature dictionary (Feature 1.8) |
| `6.TAI_LIEU/6.1.bao_cao/handoff_to_epic2.md` | EPIC 2 handoff document (Feature 1.8) |
| `6.TAI_LIEU/6.1.bao_cao/ML_READY_DATASET_VALIDATION_REPORT.md` | ML-ready validation report (Feature 1.8) |
| `6.TAI_LIEU/6.1.bao_cao/FEATURE_1_8_COMPLETION_REPORT.md` | Feature 1.8 completion report |
| `6.TAI_LIEU/6.1.bao_cao/DATA_DICTIONARY.md` | Official data dictionary (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/DATABASE_SCHEMA.md` | Database schema final (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/DATA_CLEANING_RULES.md` | Cleaning rules final (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/DATA_QUALITY_REPORT.md` | Quality report final (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/EDA_FINDINGS.md` | EDA findings summary (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/EPIC1_DEFINITION_OF_DONE_REVIEW.md` | EPIC 1 DoD review (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/EPIC1_SPRINT_REVIEW_DEMO.md` | Sprint Review demo (Feature 1.9) |
| `6.TAI_LIEU/6.1.bao_cao/FEATURE_1_9_COMPLETION_REPORT.md` | Feature 1.9 completion report |
| `6.TAI_LIEU/6.1.bao_cao/evidence/` | Terminal logs (audit trail) |
