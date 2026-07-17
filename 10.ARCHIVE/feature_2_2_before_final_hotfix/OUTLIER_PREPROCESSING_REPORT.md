# Outlier Preprocessing Report — Feature 2.2

## Default Configuration

| Parameter | Value |
|-----------|-------|
| mode | none |
| default_mode | none |

## Policy

**Baseline**: No outlier clipping applied (mode: none)

This is a conservative default that preserves all data variability. Extreme values in audio features (e.g., very high energy, very low loudness) may be musically valid.

## Extensibility

The `TrainOnlyOutlierClipper` transformer supports three modes:
1. `none` — No clipping (current default)
2. `iqr_clip` — Clip using 1.5×IQR from train data
3. `quantile_clip` — Clip using 1st/99th percentiles from train data

## Configuration Example (for future features)

```yaml
outlier_strategy:
  mode: iqr_clip  # Can be enabled per feature
  columns:
    duration_min:
      enabled: true
      lower_quantile: 0.25
      upper_quantile: 0.75
      multiplier: 1.5
```

## Leakage Prevention

✅ Thresholds computed from train split only
✅ Mode is configurable but defaults to "none" (no clipping)

---
Generated: 2026-07-17
