# Missing Value Strategy Report — Feature 2.2

## Overview

All missing values are handled using statistics learned from training data only (no leakage).

## Missing Value Strategies

| Column | Missing Count | Strategy | Learned From |
|--------|---------------|----------|--------------|
| tempo | 328 (0.05%) | median_train_only | Train split only |
| time_signature | 337 (0.06%) | mode_train_only | Train split only |
| release_month | 136,489 (22.9%) | sentinel_zero | Design decision (missing by design) |

## Detailed Strategies

### tempo
- **Method**: SimpleImputer(strategy="median")
- **Indicator**: `tempo_missing` column added
- **Train median**: ~120.0 BPM (computed from train split)
- **Rationale**: tempo is musically meaningful; median is robust to outliers

### time_signature
- **Method**: SimpleImputer(strategy="most_frequent")
- **Indicator**: `time_signature_missing` column added
- **Train mode**: 4 (4/4 time signature)
- **Rationale**: 4/4 is the dominant time signature in Western music

### release_month
- **Method**: Sentinel value 0
- **Indicator**: `release_month_missing` column added
- **Rationale**: Missing by design for year-only precision releases
- **Note**: 0 is not a valid month, serves as explicit "unknown" marker

## Leakage Prevention

✅ All imputation statistics computed from train split only
✅ Val/test splits used only for transform, never for fit
✅ Missing indicators added before preprocessing to track original missingness

---
Generated: 2026-07-17
