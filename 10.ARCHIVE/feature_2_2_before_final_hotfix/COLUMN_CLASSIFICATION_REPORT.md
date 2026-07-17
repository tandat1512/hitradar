# Column Classification Report — Feature 2.2

## Summary

All 18 baseline features have been classified by semantic role and data type.

## Column Classification

| Column | Source Type | Semantic Role | Missing Count | Missing Ratio |
|--------|-------------|---------------|---------------|---------------|
| duration_min | float64 | continuous | 0 | 0.000000 |
| explicit | bool | binary | 0 | 0.000000 |
| release_year | int64 | continuous | 0 | 0.000000 |
| release_month | int64 | categorical | 136,489 | 0.228893 |
| decade | int64 | categorical | 0 | 0.000000 |
| release_precision | int64 | categorical | 0 | 0.000000 |
| danceability | float64 | continuous | 0 | 0.000000 |
| energy | float64 | continuous | 0 | 0.000000 |
| key | int64 | categorical | 0 | 0.000000 |
| loudness | float64 | continuous | 0 | 0.000000 |
| mode | int64 | binary | 0 | 0.000000 |
| speechiness | float64 | continuous | 0 | 0.000000 |
| acousticness | float64 | continuous | 0 | 0.000000 |
| instrumentalness | float64 | continuous | 0 | 0.000000 |
| liveness | float64 | continuous | 0 | 0.000000 |
| valence | float64 | continuous | 0 | 0.000000 |
| tempo | float64 | continuous | 328 | 0.000550 |
| time_signature | float64 | categorical | 337 | 0.000565 |

## Groupings

### Continuous (11 columns)
- duration_min, release_year, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo

### Categorical (5 columns)
- release_month, decade, release_precision, key, time_signature

### Binary (2 columns)
- explicit, mode

## Special Handling

### Missing-by-Design Columns
- **release_month**: 136,489 nulls (22.9%) — Missing by design. Uses sentinel value 0.
- **tempo**: 328 nulls (0.05%) — Uses median imputation from train split.
- **time_signature**: 337 nulls (0.06%) — Uses mode imputation from train split.

### Missing Indicator Columns Added
- `tempo_missing` ✅ (LOW risk)
- `release_month_missing` ✅ (HIGH risk - temporal proxy)
- `time_signature_missing` ❌ NOT added (LOW risk - similar rates across splits)

---
Generated: 2026-07-17
