# COLUMN CLASSIFICATION REPORT

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
Phân loại chính xác 18 biến đầu vào. 0 overlap, 0 missing. Target và Identifier đã được loại trừ khỏi tập X.

## 2. Technical Evidence
| Feature | Expected Role | Actual Role | Evidence Path | Status |
|---|---|---|---|---|
| duration_min | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| release_year | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| danceability | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| energy | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| loudness | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| speechiness | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| acousticness | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| instrumentalness | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| liveness | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| valence | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| tempo | Continuous | Continuous | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| release_month | Categorical | Categorical | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| decade | Categorical | Categorical | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| release_precision | Categorical | Categorical | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| key | Categorical | Categorical | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| time_signature | Categorical | Categorical | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| explicit | Binary | Binary | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
| mode | Binary | Binary | 7.ML/7.5.preprocessing/semantic_roles.json | PASS |
