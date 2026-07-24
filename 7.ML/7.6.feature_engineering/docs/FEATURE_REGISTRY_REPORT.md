# Feature Registry Report
**Feature 2.3 - Feature Engineering Pipeline**
**Report ID:** RPT23-FEATURE-REGISTRY
**Generated:** 2026-07-19

## 1. Registry Overview

| Attribute | Value |
|-----------|-------|
| Registry ID | FR23-V1 |
| Total Features | 33 |
| Baseline Features | 18 |
| Engineered Features | 15 |
| Selected Features | 13 |
| Version | 1.0 |

## 2. Feature Categories

### 2.1 Baseline Features (18)

All 18 features from EPIC 1 baseline set (FS23-BASELINE).

### 2.2 Engineered Features (15 candidates)

| ID | Feature | Formula | Category | Selected |
|----|---------|---------|----------|----------|
| E1 | release_month_sin | sin(2π × month / 12) | time | Yes |
| E2 | release_month_cos | cos(2π × month / 12) | time | Yes |
| E3 | year_in_decade | year % 10 | time | Yes |
| E4 | duration_log | log(1 + duration) | duration | Yes |
| E5 | duration_squared | duration² | duration | Yes |
| E6 | duration_bucket | categorical | duration | No |
| E7 | energy_danceability | energy × danceability | audio | Yes |
| E8 | energy_valence | energy × valence | audio | Yes |
| E9 | danceability_valence | danceability × valence | audio | Yes |
| E10 | acousticness_instrumentalness | acousticness × instrumentalness | audio | Yes |
| E11 | energy_liveness | energy × liveness | audio | Yes |
| E12 | speechiness_explicit | speechiness × explicit | audio | Yes |
| E13 | tempo_danceability | tempo × danceability | audio | Yes |
| E14 | loudness_energy | loudness × energy | audio | Yes |
| E15 | mood_cluster | KMeans(k=5) | optional | N/A |

### 2.3 Selected Features (31)

**18 Baseline + 13 Engineered = 31 Total**

## 3. Feature Engineering Details

### 3.1 Time Features

| Feature | Type | Source | Formula |
|---------|------|--------|---------|
| release_month_sin | continuous | release_month | sin(2π × month / 12) |
| release_month_cos | continuous | release_month | cos(2π × month / 12) |
| year_in_decade | continuous | release_year | year % 10 |

### 3.2 Duration Features

| Feature | Type | Source | Notes |
|---------|------|--------|-------|
| duration_log | continuous | duration_min | log1p transform |
| duration_squared | continuous | duration_min | Squared term |

### 3.3 Audio Interaction Features

| Feature | Type | Sources | Formula |
|---------|------|---------|---------|
| energy_danceability | continuous | energy, danceability | safe_mult |
| energy_valence | continuous | energy, valence | safe_mult |
| danceability_valence | continuous | danceability, valence | safe_mult |
| acousticness_instrumentalness | continuous | acousticness, instrumentalness | safe_mult |
| energy_liveness | continuous | energy, liveness | safe_mult |
| speechiness_explicit | continuous | speechiness, explicit | safe_mult |
| tempo_danceability | continuous | tempo, danceability | safe_mult |
| loudness_energy | continuous | loudness, energy | safe_mult |

## 4. Registry Schema

```json
{
  "registry_id": "FR23-V1",
  "version": "1.0",
  "total_features": 33,
  "selected_count": 31,
  "features": [...]
}
```

## 5. Registry Files

| File | Description |
|------|-------------|
| feature_registry.json | Full registry (JSON) |
| feature_registry.csv | Feature list (CSV) |
| feature_registry_manifest.json | Registry metadata |

## 6. Data Quality

| Check | Status |
|-------|--------|
| No missing values | ✓ |
| No infinite values | ✓ |
| No duplicate features | ✓ |
| No target leakage | ✓ |
| No identifier leakage | ✓ |

## 7. Registry Integrity

| Hash | Value |
|------|-------|
| SHA-256 | Computed |

## 8. Conclusion

Feature registry complete with:
- 33 total features documented
- 31 features selected for final pipeline
- All safety checks passed
- Registry locked for reproducibility

**Status: REGISTRY COMPLETE**
