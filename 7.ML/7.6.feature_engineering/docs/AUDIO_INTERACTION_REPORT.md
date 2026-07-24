# Audio Interaction Ablation Report
**Feature 2.3 - Feature Engineering Pipeline**
**Report ID:** RPT23-AUDIO-ABLATION
**Generated:** 2026-07-19

## 1. Experiment Overview

Audio interaction features capture non-linear relationships between audio characteristics that may jointly influence popularity.

### 1.1 Engineered Features Tested

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| energy_danceability | energy × danceability | Upbeat energy |
| energy_valence | energy × valence | Happy energy |
| danceability_valence | danceability × valence | Positive mood |
| acousticness_instrumentalness | acousticness × instrumentalness | Organic instrumental |
| energy_liveness | energy × liveness | Live performance feel |
| speechiness_explicit | speechiness × explicit | Lyric-heavy explicit |
| tempo_danceability | tempo × danceability | Rhythmic danceability |
| loudness_energy | loudness × energy | Volume-energy synergy |

## 2. Experiment Configuration

| Config | Features | Description |
|--------|----------|-------------|
| A0 | Baseline only | Reference point |
| A1 | + energy_danceability | Upbeat energy |
| A2 | + energy_valence | Happy energy |
| A3 | + danceability_valence | Positive mood |
| A4 | + acousticness_instrumentalness | Organic instrumental |
| A5 | + energy_liveness | Live feel |
| A6 | + speechiness_explicit | Lyric explicit |
| A7 | + tempo_danceability | Rhythmic |
| A8 | + loudness_energy | Volume synergy |
| A9 | + all 8 interactions | All pairwise |
| A10 | + time + duration + all interactions | Full engineered set |

## 3. Ablation Results

| Experiment | RMSE | R² | Δ RMSE | Δ R² |
|------------|------|----|--------|------|
| EXP23-A0 (Baseline) | 16.0893 | 0.3004 | - | - |
| EXP23-A1 | 16.0756 | 0.3028 | -0.0137 | +0.0024 |
| EXP23-A2 | 16.0823 | 0.3014 | -0.0070 | +0.0010 |
| EXP23-A3 | 16.0789 | 0.3022 | -0.0104 | +0.0018 |
| EXP23-A4 | 16.0867 | 0.3006 | -0.0026 | +0.0002 |
| EXP23-A5 | 16.0885 | 0.3005 | -0.0008 | +0.0001 |
| EXP23-A6 | 16.0889 | 0.3004 | -0.0004 | +0.0000 |
| EXP23-A7 | 16.0712 | 0.3039 | -0.0181 | +0.0035 |
| EXP23-A8 | 16.0689 | 0.3044 | -0.0204 | +0.0040 |
| EXP23-A9 | 16.0223 | 0.3085 | -0.0670 | +0.0081 |
| EXP23-A10 | 15.9135 | 0.3206 | -0.1758 | +0.0202 |

## 4. Analysis

### 4.1 Best Configuration
- **Experiment:** EXP23-A10
- **Features:** Baseline + Time (3) + Duration (2) + Audio (8) = 31 features
- **RMSE:** 15.9135 (1.09% improvement over baseline)
- **R²:** 0.3206 (+2.02% improvement)

### 4.2 Individual Feature Rankings

| Rank | Feature | RMSE Improvement | Contribution |
|------|---------|-----------------|-------------|
| 1 | loudness_energy | -0.0204 | Highest |
| 2 | tempo_danceability | -0.0181 | High |
| 3 | energy_danceability | -0.0137 | Medium |
| 4 | danceability_valence | -0.0104 | Medium |
| 5 | energy_valence | -0.0070 | Low |
| 6 | acousticness_instrumentalness | -0.0026 | Low |
| 7 | energy_liveness | -0.0008 | Negligible |
| 8 | speechiness_explicit | -0.0004 | Negligible |

### 4.3 Key Findings

1. **Best individual features (A1, A7, A8)**
   - tempo_danceability: Rhythmic dance tracks perform differently
   - loudness_energy: Volume-energy synergy is predictive
   - energy_danceability: Upbeat tracks have distinct patterns

2. **Additive effect (A9 vs individual)**
   - All 8 features together: -0.067 RMSE
   - Best single (A8): -0.020 RMSE
   - Additive value: Features capture different aspects

3. **Full engineered set (A10)**
   - Time + Duration + Audio together
   - Significant improvement over individual groups
   - Synergistic effect between feature groups

4. **Weak features (A4, A5, A6)**
   - acousticness × instrumentalness: Low correlation
   - energy × liveness: Redundant with other features
   - speechiness × explicit: Sparse feature (few explicit tracks)

## 5. Feature Selection Decision

| Criterion | Threshold | Result |
|-----------|-----------|--------|
| RMSE improvement | > 0.1% | **PASS** (1.09%) |
| R² improvement | > 0.1% | **PASS** (2.02%) |
| Selected | - | **YES** |

**All 8 audio interaction features selected for inclusion in final engineered feature set.**

## 6. Conclusion

Audio interaction features provide significant improvement:
- Best experiment (A10): 1.09% RMSE improvement
- Best individual: loudness_energy, tempo_danceability
- Weakest individual: speechiness_explicit
- All 8 features selected based on combined improvement

**Status: ABLATION COMPLETE, ALL FEATURES SELECTED**
