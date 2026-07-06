# CLEAN TABLE VALIDATION REPORT — FEATURE 1.4

## 1. Metadata

| Field | Value |
|-------|-------|
| Database | `hitradar` @ `localhost:5432` |
| User | `postgres` |
| Date/Time | 2026-07-06 05:04 UTC |
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

## 4. release_precision Validation

| Distribution | Count |
|-------------|-------|
| day | 448,081 |
| year | 136,489 |
| month | 2,102 |

| Check | Count | Status |
|-------|-------|--------|
| Invalid precision | 0 | **PASS** |

---

## 5. Tempo / Time Signature Validation

| Check | Count | Status |
|-------|-------|--------|
| tempo <= 0 remaining | 0 | **PASS** |
| tempo IS NULL (converted) | 328 | INFO |
| time_signature = 0 remaining | 0 | **PASS** |
| time_signature IS NULL (converted) | 337 | INFO |

---

## 6. Duration Validation

| Check | Count | Status |
|-------|-------|--------|
| duration_min IS NULL | 0 | **PASS** |
| Short tracks (< 10s) | 26 | WARNING |
| Long tracks (> 60min) | 83 | WARNING |

---

## 7. FK Sanity Checks

| Check | Orphan rows | Status |
|-------|------------|--------|
| track_artists → tracks | 0 | **PASS** |
| track_artists → artists | 0 | **PASS** |
| artist_genres → artists | 0 | **PASS** |
| artist_relations → artists (src) | 0 | **PASS** |
| artist_relations → artists (tgt) | 0 | **PASS** |

---

## 8. Sample Records

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

## 9. Overall Status

**PASS**
