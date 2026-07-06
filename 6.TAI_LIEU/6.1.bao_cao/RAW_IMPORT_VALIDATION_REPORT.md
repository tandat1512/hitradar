# RAW IMPORT VALIDATION REPORT — FEATURE 1.3

> **Database:** hitradar @ localhost:5432 · **Date:** 2026-07-06 04:06 UTC
> **Overall status:** **PASS**

---

## 1. Row Count Validation

| Table | Expected | Actual | Status |
|-------|---------|--------|--------|
| `raw.raw_tracks` | 586,672 | 586,672 | **PASS** |
| `raw.raw_artists` | 1,162,095 | 1,162,095 | **PASS** |
| `raw.raw_artist_json` | 573,856 | 573,856 | **PASS** |

---

## 2. Column Validation

| Table | Expected cols | Actual cols | Columns | Status |
|-------|-------------|------------|---------|--------|
| `raw.raw_tracks` | 21 | 21 | id, name, popularity, duration_ms, explicit, artists, id_artists, release_date, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature, _import_ts | **PASS** |
| `raw.raw_artists` | 6 | 6 | id, followers, genres, name, popularity, _import_ts | **PASS** |
| `raw.raw_artist_json` | 6 | 6 | artist_id, raw_values, value_count, semantic_status, source_file, _import_ts | **PASS** |

---

## 3. ID Validation

| Column | Null count | Duplicate count | Status |
|--------|-----------|-----------------|--------|
| `raw.raw_tracks.id` | 0 | 0 | **PASS** |
| `raw.raw_artists.id` | 0 | 0 | **PASS** |
| `raw.raw_artist_json.artist_id` | 0 | 0 | **PASS** |

---

## 4. Sample Records

### raw.raw_tracks (5 rows)

| id | name | popularity | duration_ms | release_date | artists |
| --- | --- | --- | --- | --- | --- |
| 35iwgR4jXetI318WEWsa1Q | Carve | 6 | 126903 | 1922-02-22 | ['Uli'] |
| 021ht4sdgPcrDgSk7JTbKY | Capítulo 2.16 - Banquero Anarquista | 0 | 98200 | 1922-06-01 | ['Fernando Pessoa'] |
| 07A5yehtSnoedViJAZkNnc | Vivo para Quererte - Remasterizado | 0 | 181640 | 1922-03-21 | ['Ignacio Corsini'] |
| 08FmqUhxtyLTn6pAh6bk45 | El Prisionero - Remasterizado | 0 | 176907 | 1922-03-21 | ['Ignacio Corsini'] |
| 08y9GfoqCWfOGsKdwojr5e | Lady of the Evening | 0 | 163080 | 1922 | ['Dick Haymes'] |


### raw.raw_artists (5 rows)

| id | name | popularity | followers | genres |
| --- | --- | --- | --- | --- |
| 0DheY5irMjBUeLybbCUEZ2 | Armid & Amir Zare Pashai feat. Sara Rouzbehani | 0 | 0.0 | [] |
| 0DlhY15l3wsrnlfGio2bjU | ปูนา ภาวิณี | 0 | 5.0 | [] |
| 0DmRESX2JknGPQyO15yxg7 | Sadaa | 0 | 0.0 | [] |
| 0DmhnbHjm1qw6NCYPeZNgJ | Tra'gruda | 0 | 0.0 | [] |
| 0Dn11fWM7vHQ3rinvWEl4E | Ioannis Panoutsopoulos | 0 | 2.0 | [] |


### raw.raw_artist_json (5 non-empty rows)

| artist_id | value_count | semantic_status |
| --- | --- | --- |
| 0DvvojCMIqsOT1Btiwvq1h | 20 | RELATED_ARTIST_GRAPH |
| 6S3nAGEmdt4nhPrtBJ56Ga | 20 | RELATED_ARTIST_GRAPH |
| 0VLMVnVbJyJ4oyZs2L3Yl2 | 20 | RELATED_ARTIST_GRAPH |
| 0dt23bs4w8zx154C5xdVyl | 20 | RELATED_ARTIST_GRAPH |
| 0pGhoB99qpEJEsBQxgaskQ | 20 | RELATED_ARTIST_GRAPH |


---

## 5. Validation Summary

| Check | Result |
|-------|--------|
| Row counts | PASS |
| Column counts | PASS |
| ID uniqueness | PASS |
| **Overall** | **PASS** |
