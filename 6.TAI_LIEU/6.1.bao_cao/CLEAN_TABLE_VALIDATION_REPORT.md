# CLEAN TABLE VALIDATION REPORT — FEATURE 1.4
> Version: hotfix (extended checks)

## 1. Metadata

| Field | Value |
|-------|-------|
| Database | `hitradar` @ `localhost:5432` |
| User | `postgres` |
| Date/Time | 2026-07-06 05:23 UTC |
| Base directory | `X:\DUAN1\HitRadar_Pro` |
| **Overall** | **PASS** |

---

## 2. Row Count Validation (Raw vs Clean)

| Table | Raw | Clean | Status |
|-------|-----|-------|--------|
| tracks  | 586,672 | 586,672 | **PASS** |
| artists | 1,162,095 | 1,162,095 | **PASS** |

| Junction Table | Row Count | Status |
|---------------|-----------|--------|
| clean.track_artists | 730,946 | **PASS** |
| clean.genres | 5,366 | **PASS** |
| clean.artist_genres | 468,680 | **PASS** |
| clean.artist_relations | 8,864,471 | **PASS** |

---

## 3. ID Uniqueness Validation

| Table | Null IDs | Duplicate IDs | Status |
|-------|---------|--------------|--------|
| clean.tracks | 0 | 0 | **PASS** |
| clean.artists | 0 | 0 | **PASS** |

---

## 4. Missing Value Handling

> Rule: NULL is retained in clean layer — rows are NOT dropped. Status = PASS.

| Column | NULL Count | Rule | Status |
|--------|-----------|------|--------|
| clean.tracks.name | 71 | Retained NULL | **PASS** |
| clean.artists.name | 0 | Retained NULL | **PASS** |
| clean.artists.followers | 11 | Retained NULL (missing or negative) | **PASS** |

---

## 5. release_precision Validation

| Precision | Count |
|-----------|-------|
| day | 448,081 |
| year | 136,489 |
| month | 2,102 |

| Check | Count | Status |
|-------|-------|--------|
| Invalid precision | 0 | **PASS** |

---

## 6. Release Derived Column Consistency

| Check | Count | Status |
|-------|-------|--------|
| precision='year' but release_month non-null | 0 | **PASS** |
| precision='month' but release_month IS NULL | 0 | **PASS** |
| precision='day' but release_date IS NULL | 0 | **PASS** |
| release_year non-null but decade IS NULL | 0 | **PASS** |
| **Overall** | | **PASS** |

---

## 7. Tempo / Time Signature Validation

| Check | Count | Status |
|-------|-------|--------|
| tempo <= 0 remaining | 0 | **PASS** |
| tempo IS NULL (converted) | 328 | INFO |
| time_signature = 0 remaining | 0 | **PASS** |
| time_signature outside 1–5 (non-NULL) | 0 | **PASS** |
| time_signature IS NULL (converted) | 337 | INFO |
| **ts Overall** | | **PASS** |

---

## 8. Duration Validation

| Check | Count | Status |
|-------|-------|--------|
| duration_min IS NULL | 0 | **PASS** |
| Short tracks (< 10s) | 26 | WARNING |
| Long tracks (> 60min) | 83 | WARNING |

---

## 9. Audio Feature Range Validation [0, 1]

| Feature | Out-of-range count | Status |
|---------|-------------------|--------|
| danceability | 0 | **PASS** |
| energy | 0 | **PASS** |
| speechiness | 0 | **PASS** |
| acousticness | 0 | **PASS** |
| instrumentalness | 0 | **PASS** |
| liveness | 0 | **PASS** |
| valence | 0 | **PASS** |

---

## 10. Popularity Range Validation [0, 100]

| Column | Out-of-range count | Status |
|--------|-------------------|--------|
| clean.tracks.popularity | 0 | **PASS** |
| clean.artists.popularity | 0 | **PASS** |
| **Overall** | | **PASS** |

---

## 11. FK Sanity Checks

| Check | Orphan rows | Status |
|-------|------------|--------|
| track_artists → tracks | 0 | **PASS** |
| track_artists → artists | 0 | **PASS** |
| artist_genres → artists | 0 | **PASS** |
| artist_relations → artists (src) | 0 | **PASS** |
| artist_relations → artists (tgt) | 0 | **PASS** |

---

## 12. Relationship Coverage (WARNING — not structural FAIL)

### track_artists Coverage

| Metric | Value |
|--------|-------|
| Inserted into clean.track_artists | 730,946 |
| Skipped (unknown artist FK) | 26,224 |
| Estimated total parsed assignments | 757,170 |
| Coverage ratio | 96.54% |
| Skip ratio | 3.46% |
| **Status** | **WARNING — Feature 1.5 data quality gate** |

> Skipped artists are Spotify artist IDs referenced in `id_artists` but absent from `artists.csv`.
> This is expected for very niche/inactive artists. Feature 1.5 will set an acceptance threshold.

### artist_relations Coverage

| Metric | Value |
|--------|-------|
| Total raw value assignments (`raw_artist_json`) | 8,864,472 |
| Inserted distinct pairs | 8,864,471 |
| Difference | 1 |
| Likely cause | ON CONFLICT — 1 duplicate pair collapsed |
| **Status** | **WARNING — difference=1, not a data loss blocker** |

---

## 13. Sample Records

### clean.tracks

| track_id | name | popularity | duration_min | release_date | release_precision | tempo | time_signature |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1WSo0oe305PBXNQOcz9Nn2 | Tu Sei L'Unica Donna Per Me - 2005 Remaster | 49 | 3.8455 | 1979-01-01 | year | 106.318 | 4 |
| 5UBq9iGT7lfpibWr7KKqKe | Girls Talk | 49 | 3.4878 | 1979-06-09 | day | 128.843 | 4 |
| 1I4el8B1ZZKF3OGzmXDH9T | Bomber | 49 | 3.6693 | 1979-10-27 | day | 105.748 | 4 |


### clean.artists

| artist_id | name | followers | popularity |
| --- | --- | --- | --- |
| 0DheY5irMjBUeLybbCUEZ2 | Armid & Amir Zare Pashai feat. Sara Rouzbehani | 0 | 0 |
| 0DlhY15l3wsrnlfGio2bjU | ปูนา ภาวิณี | 5 | 0 |
| 0DmRESX2JknGPQyO15yxg7 | Sadaa | 0 | 0 |


### clean.track_artists

| track_id | artist_id | artist_order | is_main_artist |
| --- | --- | --- | --- |
| 1WSo0oe305PBXNQOcz9Nn2 | 7sCYC6bDTexE400qiLy4oq | 0 | True |
| 5UBq9iGT7lfpibWr7KKqKe | 65Gh3BfK84aTIugiRCgLBA | 0 | True |
| 1I4el8B1ZZKF3OGzmXDH9T | 1DFr97A9HnbV3SKTJFu62M | 0 | True |


### clean.genres

| genre_id | genre_name | normalized_genre_name |
| --- | --- | --- |
| 1 | carnaval cadiz | carnaval cadiz |
| 2 | classical harp | classical harp |
| 3 | harp | harp |


### clean.artist_genres

| artist_id | genre_id | source |
| --- | --- | --- |
| 0VLMVnVbJyJ4oyZs2L3Yl2 | 1 | artists_csv |
| 0dt23bs4w8zx154C5xdVyl | 1 | artists_csv |
| 0pGhoB99qpEJEsBQxgaskQ | 1 | artists_csv |


### clean.artist_relations

| artist_id | related_artist_id | relation_order |
| --- | --- | --- |
| 0DvvojCMIqsOT1Btiwvq1h | 3Y9UedETQztUmRuB2pYaGR | 0 |
| 0DvvojCMIqsOT1Btiwvq1h | 6ng2L9Pwj7NeXm0vJW8LLr | 1 |
| 0DvvojCMIqsOT1Btiwvq1h | 0QAlsftQZIVyNXDtK7PEt2 | 2 |


---

## 14. Overall Status

**PASS**

> Structural checks (row counts, IDs, precision, tempo/ts, duration, FK, release derived, audio range, popularity range): all PASS.
> Coverage warnings (track_artists skip ratio, artist_relations diff=1) are documented but do not block Feature 1.4 close.
