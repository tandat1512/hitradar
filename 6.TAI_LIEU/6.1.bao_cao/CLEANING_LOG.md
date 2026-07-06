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

| Warning | Count |
|---------|-------|
| duration_ms < 10,000 (short tracks) | 26 |
| duration_ms > 3,600,000 (long tracks) | 83 |
| track_artists skipped (unknown artist FK) | 26,224 |
| artist_relations skipped (unknown FK) | 0 |

---

## 5. Status

**PASS** — Clean layer populated. Proceed to validate_clean_tables.py.
