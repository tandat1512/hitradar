# Duration Feature Ablation Report
**Feature 2.3 - Feature Engineering Pipeline**
**Report ID:** RPT23-DURATION-ABLATION
**Generated:** 2026-07-19

## 1. Experiment Overview

Duration features explore how song length relates to popularity. Non-linear transformations capture different aspects of duration.

### 1.1 Engineered Features Tested

| Feature | Formula | Description |
|---------|---------|-------------|
| duration_log | log(1 + duration) | Log-transformed duration |
| duration_squared | duration² | Quadratic duration |
| duration_bucket | Categorical buckets | Short/Medium/Long/VeryLong |

### 1.2 Threshold Computation (Train-Only)

Duration buckets are computed using train split quantiles:

| Threshold | Value (minutes) |
|-----------|-----------------|
| q25 | 2.82 |
| q50 | 3.52 |
| q75 | 4.44 |

**IMPORTANT:** These thresholds are computed from train only (1900-2004) to prevent data leakage.

## 2. Experiment Configuration

| Config | Features | Description |
|--------|----------|-------------|
| D0 | Baseline only | Reference point |
| D1 | Baseline + duration_log | Log transformation |
| D2 | Baseline + duration_squared | Quadratic term |
| D3 | Baseline + duration_log + duration_squared | Both non-linear |
| D4 | Baseline + duration_bucket | Categorical buckets |

## 3. Ablation Results

| Experiment | RMSE | R² | Δ RMSE | Δ R² |
|------------|------|----|--------|------|
| EXP23-D0 (Baseline) | 16.0893 | 0.3004 | - | - |
| EXP23-D1 | 16.0812 | 0.3016 | -0.0081 | +0.0012 |
| EXP23-D2 | 16.0854 | 0.3009 | -0.0039 | +0.0005 |
| EXP23-D3 | 16.0789 | 0.3022 | -0.0104 | +0.0018 |
| EXP23-D4 | 16.0868 | 0.3007 | -0.0025 | +0.0003 |

## 4. Analysis

### 4.1 Best Configuration
- **Experiment:** EXP23-D3
- **Features:** duration_log + duration_squared
- **RMSE:** 16.0789 (0.06% improvement over baseline)
- **R²:** 0.3022 (+0.18% improvement)

### 4.2 Key Findings

1. **Log transformation is most effective (D1)**
   - Log(duration) captures diminishing returns of longer songs
   - Most impactful single duration feature

2. **Quadratic term adds marginal value (D2)**
   - Slight improvement over baseline
   - Less effective than log transformation

3. **Combined features (D3) best overall**
   - Both log and quadratic together capture different aspects
   - Additive improvement

4. **Categorical buckets (D4) least effective**
   - Information loss from binning reduces predictive power
   - Not recommended

## 5. Feature Selection Decision

| Criterion | Threshold | Result |
|-----------|-----------|--------|
| RMSE improvement | > 0.1% | FAIL (0.06%) |
| R² improvement | > 0.1% | FAIL (0.18%) |
| Selected | - | **NO** |

**Rationale:** Duration features provide marginal improvement (~0.06%) but do not meet the 0.1% threshold for standalone selection. The log transformation is more effective than quadratic or categorical approaches.

## 6. Train-Only Validation

| Check | Status |
|-------|--------|
| Thresholds from train only | ✓ PASS |
| No test data used | ✓ PASS |
| Validation split follows temporal order | ✓ PASS |

**Duration thresholds (q25, q50, q75) were computed exclusively from train data to prevent temporal leakage.**

## 7. Conclusion

Duration non-linear features provide marginal improvement:
- Best experiment (D3): 0.06% RMSE improvement
- Not sufficient for standalone selection
- Log transformation most effective among single features
- Will be evaluated in combined ablation (EXP23-A10)

**Status: ABLATION COMPLETE**
