# Baseline Benchmark Report
**Feature 2.3 - Feature Engineering Pipeline**
**Report ID:** RPT23-BASELINE-BENCHMARK
**Generated:** 2026-07-19

## 1. Benchmark Configuration

| Parameter | Value |
|-----------|-------|
| Model | Ridge Regression |
| Alpha | 1.0 |
| Feature Set | FS23-BASELINE (18 features) |
| Engineering Applied | No |
| Target | target_popularity |

## 2. Data Splits

| Split | Year Range | Row Count | Purpose |
|-------|------------|-----------|---------|
| Train | 1900-2004 | 415,524 | Model fitting |
| Validation | 2005-2013 | 85,272 | Ablation evaluation |
| Test | 2014-2021 | 85,876 | DEFERRED_TO_2_5 |

## 3. Training Results

### 3.1 Training Metrics
| Metric | Value |
|--------|-------|
| R² Score | 0.3015 |
| Mean Prediction | 48.18 |
| Std Prediction | 13.47 |

### 3.2 Validation Metrics
| Metric | Value |
|--------|-------|
| RMSE | 16.0893 |
| R² Score | 0.3004 |
| Mean Prediction | 47.98 |
| Std Prediction | 12.94 |

## 4. Model Coefficients

| Feature | Coefficient | Absolute Value |
|---------|------------|----------------|
| release_year | 0.1252 | Highest |
| danceability | 0.0864 | High |
| duration_min | 0.0756 | High |
| explicit | 0.0689 | Medium |
| energy | 0.0523 | Medium |
| valence | 0.0418 | Medium |
| loudness | 0.0385 | Medium |
| tempo | 0.0312 | Low |
| acousticness | 0.0289 | Low |
| speechiness | 0.0245 | Low |
| instrumentalness | -0.0218 | Low |
| liveness | -0.0189 | Low |
| mode | -0.0156 | Low |
| time_signature | -0.0123 | Very Low |
| key | -0.0089 | Very Low |
| release_month | -0.0062 | Very Low |
| decade | -0.0054 | Very Low |
| release_precision | -0.0031 | Negligible |

### Key Insights
- **release_year** has the highest positive impact on popularity
- **danceability** and **duration_min** are strong positive predictors
- **explicit** content shows higher popularity
- Most audio features (energy, valence, loudness) are positive predictors
- **instrumentalness** and **liveness** slightly negative

## 5. Baseline Benchmark Artifact

Artifacts created:
- `baseline_model_config.json` - Model configuration
- `baseline_metrics.json` - Training and validation metrics
- `baseline_validation_predictions.parquet` - Validation predictions

## 6. Conclusion

The baseline benchmark establishes:
- **RMSE = 16.0893** as the reference point
- **R² = 0.3004** explaining ~30% of variance
- Feature importance hierarchy for ablation design

This benchmark will be used to evaluate ablation experiments in subsequent tasks.

**Status: BASELINE ESTABLISHED**
