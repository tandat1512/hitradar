# CANDIDATE SCHEMA REPORT

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
Schema đầu ra được xác thực là đồng nhất qua 3 tập (Train, Val, Test) cho từng Candidate riêng biệt.

## 2. Technical Evidence
| Candidate | Train Shape | Val Shape | Test Shape | Output Features | Feature Hash | NaN | Inf | Status |
|---|---|---|---|---|---|---|---|---|
| P22-A | [415524, 56] | [85272, 56] | [85876, 56] | 56 | `ba3f6316` | False | False | PASS |
| P22-B | [415524, 59] | [85272, 59] | [85876, 59] | 59 | `c2498725` | False | False | PASS |
| P22-C | [415524, 56] | [85272, 56] | [85876, 56] | 56 | `ba3f6316` | False | False | PASS |
| P22-D | [415524, 18] | [85272, 18] | [85876, 18] | 18 | `e189b2e0` | False | False | PASS |
