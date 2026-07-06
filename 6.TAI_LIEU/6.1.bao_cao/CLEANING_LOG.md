# CLEANING LOG — FEATURE 1.4

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.4 — Data Cleaning & Normalization |
| Owner | Đạt |
| Database | `hitradar` @ `localhost:5432` |
| User | `postgres` |
| Date/Time | 2026-07-06 05:02 UTC |
| Duration | 738s |
| Reset clean | Yes |

---

## 2. Clean Table Row Counts

| Table | Rows | Status |
|-------|------|--------|
| `clean.tracks` | 586,672 | PASS |
| `clean.artists` | 1,162,095 | PASS |
| `clean.genres` | 5,366 | PASS |
| `clean.track_artists` | 730,946 | PASS |
| `clean.artist_genres` | 468,680 | PASS |
| `clean.artist_relations` | 8,864,471 | PASS |

---

## 3. Cleaning Rules Applied

| Rule | Applied |
|------|---------|
| tempo = 0 → NULL | Yes |
| time_signature not in 1–5 → NULL | Yes |
| release_date YYYY-MM-DD → precision=day | Yes |
| release_date YYYY-MM → YYYY-MM-01, precision=month | Yes |
| release_date YYYY → YYYY-01-01, precision=year | Yes |
| explicit 0/1 → boolean | Yes |
| duration_min = duration_ms / 60000.0 | Yes |
| artists/id_artists → ast.literal_eval | Yes |
| genres → ast.literal_eval | Yes |
| dict_artists.json → artist_relations only | Yes |
| FK filter: track_artists (skip unknown artists) | Yes |
| FK filter: artist_relations (both sides must exist) | Yes |

---

## 4. Warnings / Outliers

| Warning | Count | Xử lý |
|---------|-------|-------|
| duration_ms < 10,000 ms (short tracks) | **26** | Giữ lại theo rule — không phải lỗi, ghi warning |
| duration_ms > 3,600,000 ms (long tracks) | **83** | Giữ lại theo rule — không phải lỗi, ghi warning |
| track_artists skipped (unknown artist FK) | **26,224** | Artist ID referenced in `id_artists` nhưng không có trong `artists.csv` — coverage warning, Feature 1.5 |
| artist_relations skipped (unknown FK) | **0** | Không có orphan |

### track_artists Coverage Detail

| Metric | Value |
|--------|-------|
| Inserted into `clean.track_artists` | 730,946 |
| Skipped (artist_id not in `clean.artists`) | **26,224** |
| Estimated total parsed assignments | **757,170** |
| Coverage ratio | **96.54%** |
| Skip ratio | **3.46%** |
| Status | **WARNING** — not a blocker, Feature 1.5 sẽ set threshold |

### artist_relations Insertion Detail

| Metric | Value |
|--------|-------|
| Total raw value assignments (`SUM(raw_artist_json.value_count)`) | **8,864,472** |
| Inserted distinct pairs (`clean.artist_relations`) | **8,864,471** |
| Difference | **1** |
| Likely cause | 1 duplicate `(artist_id, related_artist_id)` pair collapsed by `ON CONFLICT DO NOTHING` |
| Status | **WARNING** — difference=1, not a data loss blocker |

---

## 5. Status

**PASS** — Clean layer populated. Validation PASS (extended checks, 15 structural checks).

> Hotfix note (2026-07-07): CLEANING_LOG updated with clarified coverage warnings.
> Duration outliers are retained per rule — NOT errors.
> track_artists 3.46% skip ratio and artist_relations diff=1 are documented warnings for Feature 1.5.
