"""
verify_dict_artists_semantic.py — Task 1.2.0
Xác minh semantic của dict_artists.json:
  - values là related artist IDs (artist_id -> related_artist_ids)?
  - hay values là genre names (artist_id -> genre list)?
Chạy: python 9.SCRIPTS/verify_dict_artists_semantic.py
Không sửa dữ liệu raw. Không tạo processed data.
"""
import sys, os, json, re

sys.stdout.reconfigure(encoding="utf-8")

RAW        = r"x:\DUAN1\HitRadar_Pro\1.DỮ_LIỆU\1.1.raw"
REPORT_OUT = r"x:\DUAN1\HitRadar_Pro\6.TAI_LIEU\6.1.bao_cao\DICT_ARTISTS_SEMANTIC_CHECK.md"

ARTISTS_CSV  = os.path.join(RAW, "artists.csv")
DICT_JSON    = os.path.join(RAW, "dict_artists.json")

# ── 1. Đọc artist IDs từ artists.csv ─────────────────────────────────────
import pandas as pd
print("Loading artists.csv id column...")
df_artists = pd.read_csv(ARTISTS_CSV, usecols=["id"], low_memory=False)
artist_id_set = set(df_artists["id"].dropna().astype(str).str.strip())
n_artist_ids = len(artist_id_set)
print(f"  artists.csv unique IDs: {n_artist_ids:,}")

# ── 2. Đọc dict_artists.json ──────────────────────────────────────────────
print("Loading dict_artists.json...")
with open(DICT_JSON, encoding="utf-8", errors="replace") as f:
    data = json.load(f)

n_keys = len(data)
print(f"  dict_artists.json keys: {n_keys:,}")

# ── 3. Sample 20 key-value pairs không rỗng ──────────────────────────────
print("Sampling 20 non-empty key-value pairs...")
samples = []
for k, v in data.items():
    if isinstance(v, list) and len(v) > 0:
        samples.append((k, v))
    if len(samples) >= 20:
        break

print(f"  Collected {len(samples)} non-empty samples")

# ── 4. Tính overlap: values vs artists.csv.id ────────────────────────────
print("Computing overlap across all non-empty values...")
SAMPLE_N = 50_000       # scan first 50k non-empty entries for overlap check

all_values_checked = []
matched = 0
total_scanned = 0

for k, v in data.items():
    if isinstance(v, list) and len(v) > 0:
        for item in v:
            if isinstance(item, str):
                all_values_checked.append(item)
                if item in artist_id_set:
                    matched += 1
                total_scanned += 1
        if total_scanned >= SAMPLE_N:
            break

overlap_ratio = matched / total_scanned if total_scanned else 0
print(f"  Values scanned (sample): {total_scanned:,}")
print(f"  Matched to artists.csv.id: {matched:,}")
print(f"  Overlap ratio: {overlap_ratio:.4%}")

# ── 5. Heuristic: kiểm tra pattern của values ─────────────────────────────
#    Spotify artist IDs: 22-char base62 (0-9, a-z, A-Z)
SPOTIFY_ID_PATTERN = re.compile(r"^[0-9A-Za-z]{22}$")

pattern_match = sum(1 for v in all_values_checked if SPOTIFY_ID_PATTERN.match(v))
pattern_ratio = pattern_match / total_scanned if total_scanned else 0
print(f"  Spotify ID pattern match (22-char alphanumeric): {pattern_match:,} / {total_scanned:,} = {pattern_ratio:.4%}")

# ── 6. Kết luận ──────────────────────────────────────────────────────────
if overlap_ratio >= 0.5 or pattern_ratio >= 0.8:
    conclusion = "RELATED_ARTIST_GRAPH"
    conclusion_text = (
        "Kết luận: `dict_artists.json` là **related artist graph** "
        "(artist_id → related_artist_ids). "
        "Không dùng làm nguồn genre. "
        "Genre pipeline chỉ dùng `artists.csv.genres`."
    )
elif overlap_ratio <= 0.05 and pattern_ratio <= 0.1:
    conclusion = "GENRE_SOURCE"
    conclusion_text = (
        "Kết luận: `dict_artists.json` có thể là **genre source** "
        "(value strings là text genre names, không match artist IDs). "
        "Cần xem lại sample để xác nhận."
    )
else:
    conclusion = "UNKNOWN_NEED_REVIEW"
    conclusion_text = (
        "Kết luận: Chưa xác định rõ. "
        "Overlap và pattern không đủ cao hoặc đủ thấp để kết luận chắc chắn. "
        "Cần xem xét thêm."
    )

print(f"\n  >>> CONCLUSION: {conclusion}")
print(f"  {conclusion_text}")

# ── 7. Sample key-values để trình bày ────────────────────────────────────
sample_display = []
for k, v in samples[:10]:
    sample_display.append({"key": k, "values_preview": v[:5], "len": len(v)})

# ── 8. Ghi DICT_ARTISTS_SEMANTIC_CHECK.md ────────────────────────────────
print(f"\nWriting report → {REPORT_OUT}")

sample_table_rows = "\n".join(
    f"| `{s['key']}` | `{s['values_preview']}` | {s['len']} |"
    for s in sample_display
)

impact_section = ""
if conclusion == "RELATED_ARTIST_GRAPH":
    impact_section = """
- **Không dùng `dict_artists.json` làm nguồn genre.**
- Genre pipeline chỉ dùng `artists.csv.genres`.
- Bảng raw: `raw.raw_artist_json` (lưu nguyên raw values để tra cứu).
- Bảng clean (nếu dùng): `clean.artist_relations(artist_id, related_artist_id)`.
- **Không tạo `clean.artist_genres` từ `dict_artists.json`.**
"""
elif conclusion == "GENRE_SOURCE":
    impact_section = """
- `dict_artists.json` có thể bổ sung genre cho `artists.csv.genres`.
- Cần đánh giá thêm chất lượng genre strings trước khi tích hợp.
- Bảng raw: `raw.raw_artist_json`.
- Bảng clean: có thể tạo `clean.artist_genres` từ cả hai nguồn nếu xác nhận.
"""
else:
    impact_section = """
- Giữ nguyên `unknown_need_review` cho dict_artists.json.
- Không thiết kế genre pipeline từ dict_artists.json cho đến khi xác minh thêm.
- Genre chỉ lấy từ `artists.csv.genres`.
"""

report = f"""# DICT_ARTISTS SEMANTIC CHECK — TASK 1.2.0

> **Mục đích:** Xác minh `dict_artists.json` là nguồn genre hay related artist graph trước khi thiết kế genre pipeline.
> **Người thực hiện:** Đạt | **Ngày:** 2026-07-05 | **Script:** `9.SCRIPTS/verify_dict_artists_semantic.py`

---

## 1. Purpose

Task 1.2.0 yêu cầu xác minh semantic meaning của `dict_artists.json` trước khi thiết kế database schema,
đặc biệt là quyết định có dùng file này làm nguồn genre hay không.

---

## 2. Inputs

| Input | File | Size |
|-------|------|------|
| Artist IDs reference | `1.DỮ_LIỆU/1.1.raw/artists.csv` | 61.89 MB |
| Target file | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | 317.17 MB |

---

## 3. Method

1. Đọc toàn bộ `artists.csv.id` → set artist IDs tham chiếu.
2. Đọc `dict_artists.json`, lấy 20 sample key-value không rỗng.
3. Scan {total_scanned:,} values đầu tiên (từ các non-empty entries).
4. Tính overlap giữa values và `artists.csv.id`.
5. Kiểm tra pattern 22-char alphanumeric (Spotify Artist ID format).
6. Kết luận dựa trên overlap ratio và pattern ratio.

---

## 4. Results

| Chỉ số | Giá trị |
|--------|---------|
| `artists.csv` unique IDs | {n_artist_ids:,} |
| `dict_artists.json` keys | {n_keys:,} |
| Values scanned (sample) | {total_scanned:,} |
| Matched to `artists.csv.id` | {matched:,} |
| **Overlap ratio** | **{overlap_ratio:.2%}** |
| 22-char pattern match | {pattern_match:,} / {total_scanned:,} = {pattern_ratio:.2%} |

### Sample key-values (10 non-empty entries)

| Key (artist_id) | Values (preview, max 5) | Value count |
|----------------|------------------------|-------------|
{sample_table_rows}

---

## 5. Conclusion

**{conclusion}**

{conclusion_text}

| Tiêu chí | Kết quả |
|---------|---------|
| Overlap với `artists.csv.id` | {overlap_ratio:.2%} |
| Spotify ID pattern (22-char) | {pattern_ratio:.2%} |
| Sample values có phải text genre (pop/rock/...)? | {"Không — trông như artist IDs" if conclusion == "RELATED_ARTIST_GRAPH" else "Cần kiểm tra thêm"} |

---

## 6. Impact on Database Design

{impact_section}

---

## 7. Updated Data Contract Note

| File | Vai trò trước khi verify | Vai trò sau khi verify |
|------|--------------------------|------------------------|
| `dict_artists.json` | `unknown_need_review` | **{conclusion}** |
| `artists.csv.genres` | Nguồn genre chính | **Nguồn genre duy nhất được xác nhận** |
"""

with open(REPORT_OUT, "w", encoding="utf-8") as f:
    f.write(report)

print(f"Done. Report saved to: {REPORT_OUT}")
print(f"\n=== SUMMARY ===")
print(f"Conclusion       : {conclusion}")
print(f"Overlap ratio    : {overlap_ratio:.2%}")
print(f"Pattern ratio    : {pattern_ratio:.2%}")
print(f"Genre source     : artists.csv.genres only")
