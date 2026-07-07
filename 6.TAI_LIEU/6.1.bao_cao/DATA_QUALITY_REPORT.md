# DATA QUALITY REPORT — FEATURE 1.5

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.5 — Data Quality Gates |
| Owner | Đạt |
| Database | `hitradar` @ `localhost:5432` |
| User | `postgres` |
| Date/Time | 2026-07-07 15:05 UTC |
| Script | `9.SCRIPTS/run_data_quality_gates.py` |
| SQL | `2.DATABASE_SQL/2.3.lam_sach/03_data_quality_gates.sql` |
| **Overall** | **PASS_WITH_WARNINGS** |

---

## 2. Executive Summary

| Metric | Count |
|--------|-------|
| Total Gates | 12 |
| PASS | 10 |
| WARNING | 2 |
| FAIL | 0 |
| **Overall** | **PASS_WITH_WARNINGS** |

---

## 3. Gate Results

| Gate ID | Gate Name | Result | Key Metrics | Severity Logic |
|---------|-----------|--------|-------------|----------------|
| G01 | Null Ratio | **PASS** | ID null=0 | name null=71 | followers null=11 | ID null → FAIL; name/followers null → INFO |
| G02 | Duplicate Report | **PASS** | All duplicates = 0 | Any dup → FAIL |
| G03 | Audio Feature Range | **PASS** | All 7 audio features: OOR = 0 | Any OOR → FAIL |
| G04 | Popularity Range | **PASS** | tracks OOR=0 | artists OOR=0 | Any OOR → FAIL |
| G05 | Duration Validity | **WARNING** | invalid ms=0 | null min=0 | short=26 | long=83 | invalid/null → FAIL; outliers → WARNING |
| G06 | Tempo / Loudness | **WARNING** | tempo invalid=0 | loud<-60=0 | loud>10=0 | loud>0=219 | tempo<=0 or loud OOR → FAIL; loud>0 → WARNING |
| G07 | Release Date | **PASS** | invalid prec=0 | yr<1900=0 | yr>2025=0 | derived inconsist=0 | invalid prec/derived → FAIL; yr range → WARNING |
| G08 | Artist Join Coverage | **PASS** | 96.54% (730,946/757,170) | ≥95% PASS; 90–95% WARNING; <90% FAIL |
| G09 | Genre Join Coverage | **PASS** | 100.00% (305,595/305,595) | ≥99% PASS; 95–99% WARNING; <95% FAIL |
| G10 | Row Count Pre/Post | **PASS** | tracks 586,672=586,672 | artists 1,162,095=1,162,095 | mismatch → FAIL |
| G11 | FK / Orphan Checks | **PASS** | All 6 orphan checks = 0 | Any orphan → FAIL |
| G12 | ML-safe Notes | **PASS** | Documented: target/dashboard_only/caution | Always PASS (informational) |

---

## 4. Null Ratio Checks (G01)

| Column | Null Count | % of Total | Rule | Status |
|--------|-----------|-----------|------|--------|
| `clean.tracks.track_id` | 0 | 0.000% | FAIL if > 0 | **PASS** |
| `clean.artists.artist_id` | 0 | 0.000% | FAIL if > 0 | **PASS** |
| `clean.tracks.name` | 71 | 0.012% | Retained NULL | **INFO** |
| `clean.artists.name` | 0 | — | Retained NULL | **INFO** |
| `clean.artists.name` (empty) | 0 | — | Empty string after trim | **INFO** |
| `clean.artists.followers` | 11 | — | Retained NULL | **INFO** |

---

## 5. Duplicate Checks (G02)

| Column / Composite | Duplicate Count | Status |
|-------------------|----------------|--------|
| `clean.tracks.track_id` | 0 | **PASS** |
| `clean.artists.artist_id` | 0 | **PASS** |
| `clean.genres.genre_name` | 0 | **PASS** |
| `clean.genres.normalized_genre_name` | 0 | **PASS** |
| `clean.track_artists (track_id, artist_id)` | 0 | **PASS** |
| `clean.artist_genres (artist_id, genre_id)` | 0 | **PASS** |
| `clean.artist_relations (artist_id, related_artist_id)` | 0 | **PASS** |

---

## 6. Range Checks

### G03 — Audio Features [0, 1]

| Feature | Out-of-range | Status |
|---------|-------------|--------|
| danceability | 0 | **PASS** |
| energy | 0 | **PASS** |
| speechiness | 0 | **PASS** |
| acousticness | 0 | **PASS** |
| instrumentalness | 0 | **PASS** |
| liveness | 0 | **PASS** |
| valence | 0 | **PASS** |

### G04 — Popularity [0, 100]

| Column | Out-of-range | Status |
|--------|-------------|--------|
| `clean.tracks.popularity` | 0 | **PASS** |
| `clean.artists.popularity` | 0 | **PASS** |

> **ML Note:** `clean.tracks.popularity` is the **target variable** — do NOT use as ML input feature.
> `clean.artists.popularity` is **dashboard_only / caution**.

### G05 — Duration

| Check | Count | Status |
|-------|-------|--------|
| `duration_ms <= 0` | 0 | **PASS** |
| `duration_min IS NULL` | 0 | **PASS** |
| Short tracks (< 10s) | 26 | **WARNING** |
| Long tracks (> 60min) | 83 | **WARNING** |

### G06 — Tempo / Loudness

| Check | Count | Status |
|-------|-------|--------|
| `tempo <= 0` remaining | 0 | **PASS** |
| `tempo IS NULL` (converted from 0) | 328 | INFO |
| `loudness < -60` | 0 | **PASS** |
| `loudness > 10` | 0 | **PASS** |
| `loudness > 0` (unusual) | 219 | **WARNING** |
| `loudness IS NULL` | 0 | INFO |

---

## 7. Release Date Consistency (G07)

| Check | Count | Status |
|-------|-------|--------|
| Invalid `release_precision` | 0 | **PASS** |
| `release_year < 1900` | 0 | **PASS** |
| `release_year > 2025` | 0 | **PASS** |
| `precision='year'` AND `release_month != NULL` | 0 | **PASS** |
| `precision='month'` AND `release_month IS NULL` | 0 | **PASS** |
| `release_year != NULL` AND `decade IS NULL` | 0 | **PASS** |

### Release Precision Distribution

| Precision | Count |
|-----------|-------|
| day | 448,081 |
| year | 136,489 |
| month | 2,102 |

---

## 8. Join Coverage

### G08 — Artist Join Coverage

| Metric | Value |
|--------|-------|
| Inserted into `clean.track_artists` | 730,946 |
| Skipped (unknown artist FK, Feature 1.4) | 26,224 |
| Estimated total parsed assignments | 757,170 |
| **Coverage ratio** | **96.54%** |
| Gate threshold | ≥ 95% = PASS, 90–95% = WARNING, < 90% = FAIL |
| **Gate result** | **PASS** |

### G09 — Genre Join Coverage

| Metric | Value |
|--------|-------|
| Artists with non-empty genres (raw) | 305,595 |
| Artists mapped to genre in `clean.artist_genres` | 305,595 |
| **Coverage ratio** | **100.00%** |
| `artist_genres` orphan artist_id | 0 |
| `artist_genres` orphan genre_id | 0 |
| Gate threshold | ≥ 99% = PASS, 95–99% = WARNING, < 95% = FAIL |
| **Gate result** | **PASS** |

---

## 9. Row Count Pre/Post Clean (G10)

| Table | Raw | Clean | Status |
|-------|-----|-------|--------|
| tracks | 586,672 | 586,672 | **PASS** |
| artists | 1,162,095 | 1,162,095 | **PASS** |

| Junction Table | Row Count | Status |
|---------------|-----------|--------|
| clean.track_artists | 730,946 | **PASS** |
| clean.genres | 5,366 | **PASS** |
| clean.artist_genres | 468,680 | **PASS** |
| clean.artist_relations | 8,864,471 | **PASS** |

---

## 10. FK / Orphan Checks (G11)

| Check | Orphan rows | Status |
|-------|------------|--------|
| track_artists → tracks | 0 | **PASS** |
| track_artists → artists | 0 | **PASS** |
| artist_genres → artists | 0 | **PASS** |
| artist_genres → genres | 0 | **PASS** |
| artist_relations → artists(src) | 0 | **PASS** |
| artist_relations → artists(tgt) | 0 | **PASS** |

---

## 11. ML-safe Notes (G12)

| Column | ML Role |
|--------|---------|
| `tracks.popularity` | TARGET variable — do NOT use as input feature |
| `artists.popularity` | dashboard_only — caution for ML use |
| `artists.followers` | caution — may contain NULL; do not use without imputation |
| `aggregate_popularity` | NOT computed in EPIC 1 |
| `train_test_split` | NOT done in EPIC 1 |

---

## 12. Warnings to Carry Forward

- **G08**: track_artists skipped = 26,224 (3.46%) — Feature 1.5 gate PASS (96.54%)
- **G05**: Short tracks (<10s) = 26; long tracks (>60min) = 83
- **F14 carry-forward**: artist_relations diff = 1 (ON CONFLICT duplicate pair collapsed)
- **G01**: tracks.name NULL = 71 (retained by rule)
- **G01**: artists.followers NULL = 11 (retained by rule)
- **G06**: loudness > 0 = 219 (unusual but valid per rule)

---

## 13. Decision

See overall status.

**Overall: PASS_WITH_WARNINGS**
