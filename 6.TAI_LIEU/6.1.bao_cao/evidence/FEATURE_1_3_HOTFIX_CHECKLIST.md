# FEATURE 1.3 HOTFIX CHECKLIST

> **Feature:** 1.3 — Data Ingestion Pipeline
> **Loại:** Hotfix / Code Hardening
> **Ngày:** 2026-07-07
> **Owner:** Đạt

---

## Code hardening

| Hạng mục | Trạng thái |
|---------|-----------|
| `import_raw_data.py` — không còn hard-coded absolute project path | **PASS** |
| `validate_raw_import.py` — không còn hard-coded absolute project path | **PASS** |
| `--base-dir` argument được hỗ trợ trong cả 2 scripts | **PASS** |
| `PGPASSWORD` required, không hardcode password | **PASS** |
| `LOG_DIR.mkdir(parents=True, exist_ok=True)` trong cả 2 scripts | **PASS** |

---

## Failure behavior

| Hạng mục | Trạng thái |
|---------|-----------|
| Missing `clean.tracks.release_precision` gây FAIL (dừng chương trình) | **PASS** |
| Row count mismatch gây FAIL trong import log và console | **PASS** |
| Column count mismatch gây FAIL trong validation report | **PASS** |
| Overall validation = FAIL nếu bất kỳ check nào FAIL | **PASS** |
| `validate_raw_import.py` exit code 1 khi overall FAIL | **PASS** |

---

## Documentation

| Hạng mục | Trạng thái |
|---------|-----------|
| `HOW_TO_RUN_DATA_PIPELINE.md` dùng `-v ON_ERROR_STOP=1` cho psql | **PASS** |
| DDL file order explicit (01→05) thay vì wildcard | **PASS** |
| Dùng `$project` variable thay hardcode path | **PASS** |
| Evidence log location được document | **PASS** |
| User/database conventions ghi rõ | **PASS** |
| `FEATURE_1_3_COMPLETION_REPORT.md` cập nhật PASS — REPRODUCIBLE PIPELINE VERIFIED | **PASS** |

---

## Import baseline (unchanged)

| Table | Rows | Status |
|-------|------|--------|
| `raw.raw_tracks` | 586,672 | PASS |
| `raw.raw_artists` | 1,162,095 | PASS |
| `raw.raw_artist_json` | 573,856 | PASS |

> Row counts không thay đổi — import không chạy lại trong hotfix này.
> "Code hardening completed. Existing import validation remains PASS."

---

## Evidence logs

Nếu muốn lưu terminal output làm audit trail, chạy:

```powershell
$project = "X:\DUAN1\HitRadar_Pro"
$ev      = "$project\6.TAI_LIEU\6.1.bao_cao\evidence"

python "$project\9.SCRIPTS\import_raw_data.py" --base-dir $project --database hitradar --user postgres --reset |
    Tee-Object -FilePath "$ev\feature_1_3_import_terminal_log.txt"

python "$project\9.SCRIPTS\validate_raw_import.py" --base-dir $project --database hitradar --user postgres |
    Tee-Object -FilePath "$ev\feature_1_3_validation_terminal_log.txt"
```

> Các file `.txt` này được gitignore.

---

## Final status

**PASS**

Tất cả 15 hạng mục hotfix: PASS.
Pipeline tái lập được — người khác có thể chạy theo `HOW_TO_RUN_DATA_PIPELINE.md`.
