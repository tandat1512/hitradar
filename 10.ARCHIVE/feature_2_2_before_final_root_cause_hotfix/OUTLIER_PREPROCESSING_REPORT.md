# OUTLIER PREPROCESSING REPORT

**Feature 2.2 — Leakage-Safe Preprocessing Pipeline**
**HitRadar Pro — EPIC 2**

**Repository URL**: https://github.com/tandat1512/hitradar.git
**Source Branch**: main
**Source Commit Used for Generation**: 1352fc050d73796e67620d5fd63d44661f2172f2
**Source Commit Timestamp**: 2026-07-18 14:29:58 +0700
**Working Tree Status**: DIRTY
**Generator Path**: 9.SCRIPTS/feature_2_2_preprocessing.py
**Generator SHA-256**: 2bf4f510d987b65b5b0206376a651f43dfa64ab97996973dba0447c740181fdf
**Generated Timestamp**: 2026-07-18T10:33:13.118872+00:00
**Data Version**: ml-ready-2026-07-17-v1
**Split Version**: temporal-split-v1
**Test Summary Path**: 7.ML/7.5.preprocessing/feature_2_2_test_summary.json
**JUnit XML Path**: 7.ML/7.5.preprocessing/pytest_feature_2_2.xml
**Report Manifest Path**: 7.ML/7.5.preprocessing/feature_2_2_report_manifest.json
**Closure Gate Path**: 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json

---

## 1. Kết luận điều hành
Outlier Clipping sử dụng phân vị (IQR) chỉ tính trên tập Train (TRAIN_IQR_CLIP).

## 2. Technical Evidence
| Feature | Method | Lower | Upper | Fit Split | Evidence Path | Status |
|---|---|---|---|---|---|---|
| duration_min | TRAIN_IQR_CLIP | 0.39 | 6.87 | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | PASS |
| tempo | TRAIN_IQR_CLIP | 33.36 | 196.10 | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | PASS |
| loudness | TRAIN_IQR_CLIP | -23.57 | 1.75 | train | 7.ML/7.5.preprocessing/outlier_thresholds.json | PASS |
