# ENCODING STRATEGY REPORT

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
Encoding Categorical sử dụng OneHotEncoder và OrdinalEncoder, đảm bảo không sập khi gặp category mới (handle_unknown).

## 2. Technical Evidence
| Candidate | Feature | Encoder | Categories | Fit Split | Evidence Path | Status |
|---|---|---|---|---|---|---|
| P22-A | release_month | OneHotEncoder | 13 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-A | decade | OneHotEncoder | 10 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-A | release_precision | OneHotEncoder | 3 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-A | key | OneHotEncoder | 12 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-A | time_signature | OneHotEncoder | 5 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-B | release_month | OneHotEncoder | 13 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-B | decade | OneHotEncoder | 10 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-B | release_precision | OneHotEncoder | 3 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-B | key | OneHotEncoder | 12 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-B | time_signature | OneHotEncoder | 5 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-C | release_month | OneHotEncoder | 13 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-C | decade | OneHotEncoder | 10 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-C | release_precision | OneHotEncoder | 3 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-C | key | OneHotEncoder | 12 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-C | time_signature | OneHotEncoder | 5 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-D | release_month | OrdinalEncoder | 13 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-D | decade | OrdinalEncoder | 10 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-D | release_precision | OrdinalEncoder | 3 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-D | key | OrdinalEncoder | 12 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
| P22-D | time_signature | OrdinalEncoder | 5 classes | train | 7.ML/7.5.preprocessing/encoder_categories.json | PASS |
