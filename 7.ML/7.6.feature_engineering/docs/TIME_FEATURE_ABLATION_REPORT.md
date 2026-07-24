# Time Feature Ablation Report
**Feature 2.3 - Feature Engineering Pipeline**
**Report ID:** RPT23-TIME-ABLATION
**Generated:** 2026-07-19

## 1. Experiment Overview

Time features capture temporal patterns in song releases that may correlate with popularity.

### 1.1 Engineered Features Tested

| Feature | Formula | Description |
|---------|---------|-------------|
| release_month_sin | sin(2π × month / 12) | Cyclical month (sine) |
| release_month_cos | cos(2π × month / 12) | Cyclical month (cosine) |
| year_in_decade | year % 10 | Position within decade |

## 2. Experiment Configuration

| Config | Features | Description |
|--------|----------|-------------|
| T0 | Baseline only | Reference point |
| T1 | Baseline + month_sin | Cyclical month sin |
| T2 | Baseline + month_cos | Cyclical month cos |
| T3 | Baseline + both cyclical | Sin + Cos together |
| T4 | Baseline + year_in_decade | Decade position |

## 3. Ablation Results

| Experiment | RMSE | R² | Δ RMSE | Δ R² |
|------------|------|----|--------|------|
| EXP23-T0 (Baseline) | 16.0893 | 0.3004 | - | - |
| EXP23-T1 | 16.0847 | 0.3012 | -0.0046 | +0.0008 |
| EXP23-T2 | 16.0876 | 0.3007 | -0.0017 | +0.0003 |
| EXP23-T3 | 16.0772 | 0.3025 | -0.0121 | +0.0021 |
| EXP23-T4 | 16.0891 | 0.3005 | -0.0002 | +0.0001 |

## 4. Analysis

### 4.1 Best Configuration
- **Experiment:** EXP23-T3
- **Features:** release_month_sin + release_month_cos
- **RMSE:** 16.0772 (0.08% improvement over baseline)
- **R²:** 0.3025 (+0.21% improvement)

### 4.2 Key Findings

1. **Cyclical encoding outperforms raw features**
   - T3 (sin+cos) improves more than T4 (year_in_decade)
   - Cyclical encoding captures seasonal patterns better

2. **Month matters slightly**
   - Release month has a weak but measurable impact on popularity
   - The cyclical representation (T3) is more effective than individual components (T1, T2)

3. **Year position in decade (T4) is negligible**
   - Year-in-decade adds virtually no predictive value
   - Already captured by release_year and decade features

## 5. Feature Selection Decision

| Criterion | Threshold | Result |
|-----------|-----------|--------|
| RMSE improvement | > 0.1% | FAIL (0.08%) |
| R² improvement | > 0.1% | FAIL (0.21%) |
| Selected | - | **NO** |

**Rationale:** While T3 shows improvement, it does not meet the 0.1% RMSE improvement threshold for standalone selection. However, these features may be included in combination with other engineered features.

## 6. Conclusion

Time features (cyclical month encoding) provide marginal improvement:
- Best experiment (T3): 0.08% RMSE improvement
- Not sufficient for standalone selection
- Will be evaluated in combined ablation (EXP23-A10)

**Status: ABLATION COMPLETE**
