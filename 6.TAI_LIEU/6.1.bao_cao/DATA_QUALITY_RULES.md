# DATA QUALITY RULES — FEATURE 1.5

## 1. Purpose

Feature 1.5 kiểm định clean layer (output của Feature 1.4) trước khi cho phép chuyển sang:
- **Feature 1.6** — Analytics Views & Indexes
- **Feature 1.8** — ML-safe Handoff

Các gates định nghĩa tiêu chuẩn tối thiểu về tính đầy đủ, tính nhất quán, và phạm vi hợp lệ của dữ liệu trong clean layer. Gate FAIL sẽ chặn pipeline, yêu cầu quay lại Feature 1.4 hoặc mở Feature 1.5 follow-up.

Script: `9.SCRIPTS/run_data_quality_gates.py`
SQL:    `2.DATABASE_SQL/2.3.lam_sach/03_data_quality_gates.sql`

---

## 2. Gate Severity Definitions

| Severity | Ý nghĩa | Hành động |
|----------|---------|-----------|
| **PASS** | Đạt chuẩn | Tiếp tục pipeline |
| **WARNING** | Chưa chặn pipeline nhưng cần carry forward và theo dõi | Tiếp tục nhưng phải ghi rõ warning |
| **FAIL** | Không được chuyển Feature 1.6 trước khi xử lý | Quay lại Feature 1.4 hoặc mở Feature 1.5 follow-up |

---

## 3. Gate Registry

| Gate ID | Gate Name | Check Logic | PASS | WARNING | FAIL | Applies To | Reason |
|---------|-----------|-------------|------|---------|------|-----------|--------|
| **G01** | Null ratio | ID cols null=0; name/followers null được phép nhưng phải report | null_id=0 | name_null>0 (info) | null_id>0 | clean.tracks, clean.artists | ID null = data integrity violation |
| **G02** | Duplicate report | track_id/artist_id/genre_name dup=0; junction composite dup=0 | all dup=0 | — | any dup>0 | All clean tables | Duplicate IDs corrupt joins and analytics |
| **G03** | Audio features range | danceability/energy/speechiness/acousticness/instrumentalness/liveness/valence ∈ [0,1] | oor=0 | — | oor>0 | clean.tracks | Out-of-range values invalid for ML/analytics |
| **G04** | Popularity range | tracks.popularity ∈ [0,100]; artists.popularity ∈ [0,100] | oor=0 | — | oor>0 | clean.tracks, clean.artists | Out-of-range popularity invalid |
| **G05** | Duration validity | duration_ms>0; duration_min NOT NULL; outliers ghi warning | duration_ms>0 AND duration_min NOT NULL | ms<10,000 or ms>3,600,000 (count) | duration_ms<=0 OR duration_min NULL | clean.tracks | Duration invalid làm analytics sai |
| **G06** | Tempo / loudness | tempo<=0 remaining=0; loudness ∈ [-60, 10] | tempo<=0 cnt=0 AND loudness in range | loudness>0 count (unusual) | tempo<=0 cnt>0 OR loudness<-60 OR loudness>10 | clean.tracks | Extreme outliers corrupt audio analysis |
| **G07** | Year / release consistency | precision ∈ {day,month,year,unknown}; release_year ∈ [1900,2025]; derived cols consistent | invalid=0 | release_year<1900 or >2025 count (info) | invalid_precision>0 OR derived inconsistency>0 | clean.tracks | Incorrect dates break time-series analysis |
| **G08** | Artist join coverage | track_artists/estimated_parsed ≥ 95% | ≥ 95% | 90–95% | < 90% | clean.track_artists | Low coverage = many tracks lose artist info |
| **G09** | Genre join coverage | artist_genres/artists_with_genres ≥ 99% | ≥ 99% | 95–99% | < 95% | clean.artist_genres | Low coverage = genre analysis unreliable |
| **G10** | Row count pre/post clean | clean.tracks=raw.raw_tracks; clean.artists=raw.raw_artists | counts equal | — | counts differ | clean.tracks, clean.artists | Row loss = data completeness violation |
| **G11** | FK / orphan checks | 0 orphan records in all junction tables | orphans=0 | — | orphans>0 | All junction tables | Orphan FK = join corruption |
| **G12** | ML-safe notes | popularity label check; no aggregate features; no train/test split | documented | — | — | clean.tracks, clean.artists | Prevent label leakage in future ML work |

---

## 4. Gate Detail Specifications

### G01 — Null Ratio

**ID columns must be 0 null** (FAIL if violated):
- `clean.tracks.track_id IS NULL`
- `clean.artists.artist_id IS NULL`

**Name/followers null are permitted by rule** (PASS, report count):
- `clean.tracks.name IS NULL` → WARNING info (expected: small number)
- `clean.artists.name IS NULL` → WARNING info
- `clean.artists.name = ''` after trim → WARNING info
- `clean.artists.followers IS NULL` → WARNING info (missing/negative in source)

---

### G02 — Duplicate Report

Zero duplicates required (FAIL if violated):
- `track_id` duplicate in `clean.tracks`
- `artist_id` duplicate in `clean.artists`
- `genre_name` duplicate in `clean.genres`
- `normalized_genre_name` duplicate in `clean.genres`
- Composite `(track_id, artist_id)` in `clean.track_artists`
- Composite `(artist_id, genre_id)` in `clean.artist_genres`
- Composite `(artist_id, related_artist_id)` in `clean.artist_relations`

---

### G03 — Audio Features Range

Valid range = [0.0, 1.0]. Out-of-range = FAIL.

Features checked:
- `danceability`, `energy`, `speechiness`, `acousticness`
- `instrumentalness`, `liveness`, `valence`

NULL values are permitted (some tracks have no audio analysis).

---

### G04 — Popularity Range

Valid range = [0, 100]. Out-of-range = FAIL.

**Important ML Note:**
- `clean.tracks.popularity` → **target variable** for popularity prediction
- `clean.artists.popularity` → **dashboard_only / caution** (do NOT use as ML input feature in EPIC 1)

---

### G05 — Duration Validity

| Sub-check | Threshold | Severity |
|-----------|-----------|---------|
| `duration_ms <= 0` | count = 0 | FAIL |
| `duration_min IS NULL` | count = 0 | FAIL |
| `duration_ms < 10,000` | count > 0 | WARNING |
| `duration_ms > 3,600,000` | count > 0 | WARNING |

Duration outliers (short/long) are kept per Feature 1.4 cleaning rule. They are not errors but must be reported for downstream filtering.

---

### G06 — Tempo / Loudness

| Sub-check | Threshold | Severity |
|-----------|-----------|---------|
| `tempo <= 0` remaining | count = 0 | FAIL if > 0 |
| `tempo IS NULL` | any count | INFO (converted from 0) |
| `loudness < -60` | count = 0 | FAIL |
| `loudness > 10` | count = 0 | FAIL |
| `loudness > 0` | count > 0 | WARNING (unusual but possible) |

---

### G07 — Year / Release Date Consistency

| Sub-check | Threshold | Severity |
|-----------|-----------|---------|
| Invalid `release_precision` (not in day/month/year/unknown) | = 0 | FAIL |
| `release_year < 1900` | = 0 | WARNING info |
| `release_year > 2025` | = 0 | WARNING info |
| `precision='year'` AND `release_month IS NOT NULL` | = 0 | FAIL |
| `precision='month'` AND `release_month IS NULL` | = 0 | FAIL |
| `release_year IS NOT NULL` AND `decade IS NULL` | = 0 | FAIL |

---

### G08 — Artist Join Coverage

```
coverage = clean.track_artists / (clean.track_artists + 26,224 skipped)
         = 730,946 / 757,170 = 96.54%  (Feature 1.4 baseline)
```

| Coverage | Severity |
|----------|---------|
| ≥ 95% | PASS |
| 90%–95% | WARNING |
| < 90% | FAIL |

The `26,224` skipped figure comes from the Feature 1.4 cleaning log (FK filter: artist_id referenced in `id_artists` but absent from `artists.csv`).

---

### G09 — Genre Join Coverage

```
artists_with_non_empty_genres = COUNT(*) FROM raw.raw_artists
                                 WHERE genres IS NOT NULL AND genres <> '[]'
coverage = COUNT(DISTINCT artist_id FROM clean.artist_genres) / artists_with_non_empty_genres
```

| Coverage | Severity |
|----------|---------|
| ≥ 99% | PASS |
| 95%–99% | WARNING |
| < 95% | FAIL |

---

### G10 — Row Count Pre/Post Clean

| Check | Severity |
|-------|---------|
| `clean.tracks ≠ raw.raw_tracks` | FAIL |
| `clean.artists ≠ raw.raw_artists` | FAIL |
| Any junction table = 0 | FAIL |

---

### G11 — FK / Orphan Checks

Zero orphans required (FAIL if any > 0):
- `clean.track_artists` → `clean.tracks`
- `clean.track_artists` → `clean.artists`
- `clean.artist_genres` → `clean.artists`
- `clean.artist_genres` → `clean.genres`
- `clean.artist_relations` → `clean.artists` (source)
- `clean.artist_relations` → `clean.artists` (target)

---

### G12 — ML-safe Notes

This gate is informational only (always PASS). Records the ML usage policy for Feature 1.8.

| Column | ML Role | Note |
|--------|---------|------|
| `clean.tracks.popularity` | **target** | Prediction target — do NOT use as input feature |
| `clean.artists.popularity` | **dashboard_only** | Aggregated stat — caution for ML use |
| `clean.artists.followers` | **caution** | May contain NULL and extreme values |
| Aggregate popularity over artists | **forbidden** | Not computed in EPIC 1 |
| Train/test split | **not done** | EPIC 1 scope ends at clean data handoff |

---

## 5. Carry-Forward Warnings (from Feature 1.4)

These warnings were established in Feature 1.4 and must be re-confirmed in Feature 1.5:

| Warning | Value | Action |
|---------|-------|--------|
| `track_artists` skipped (unknown artist FK) | 26,224 (3.46%) | G08 threshold check |
| `artist_relations` diff (ON CONFLICT) | 1 | Informational |
| Duration short outliers | 26 | G05 WARNING |
| Duration long outliers | 83 | G05 WARNING |
| `tracks.name` NULL | 71 | G01 INFO |
| `artists.followers` NULL | 11 | G01 INFO |
