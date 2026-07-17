# FEATURE 2.1 HOTFIX REPORT

**Feature 2.1 — Data Intake, Validation & Temporal Split**
**HitRadar Pro — EPIC 2**
**Generated**: 2026-07-16T12:29:23.423707+00:00

---

## 1. Hotfix Summary

| Property | Value |
|---|---|
| Hotfix version | 1.0 |
| Bugs found | 9 |
| Bugs fixed | 9 |
| Files created | 18 |
| Files modified | 4 |
| Files archived | Pre-hotfix artifacts in `10.ARCHIVE/feature_2_1_pre_hotfix/` |
| Data version | UNCHANGED (`ml-ready-2026-07-16-v1`) |
| Split boundaries | UNCHANGED (1900-2004/2005-2013/2014-2021) |
| Split ID files | NOT regenerated (boundaries unchanged, hashes match) |

---

## 2. Bugs Fixed

| # | Bug ID | Severity | Description |
|---|---|---|---|
| 1 | BUG-001 | MEDIUM | Candidate split zero counts reused across candidates |
| 2 | BUG-002 | HIGH | Year 1900 not flagged as contract deviation |
| 3 | BUG-003 | HIGH | test_set_lock.json missing governance fields |
| 4 | BUG-004 | MEDIUM | Incorrect "test never opened" language |
| 5 | BUG-005 | MEDIUM | Legacy .pkl files not quarantined |
| 6 | BUG-006 | HIGH | Validation only checked file existence |
| 7 | BUG-007 | HIGH | Temporal shift PSI>1.5 labeled "expected warning" |
| 8 | BUG-008 | MEDIUM | release_month_missing temporal proxy undocumented |
| 9 | BUG-009 | HIGH | "50/50 PASS" claim before semantic checks |

---

## 3. Validation Results

| Metric | Pre-Hotfix | Post-Hotfix |
|---|---|---|
| Total checks | 50 (existence only) | **93** (content-level) |
| PASS | 50 | **93** |
| FAIL | 0 | **0** |
| Check quality | File existence | Schema, hash, content, union, intersection |
| Temporal shift severity | "Expected warning" | **HIGH** |
| Year anomaly | Unreported | Registered as exception |
| Test governance | Incomplete lock | Full governance doc |
| Legacy artifacts | "Pre-existing, ignored" | Quarantined with manifest |

---

## 4. Reports Created

| # | File | Type |
|---|---|---|
| 1 | RELEASE_YEAR_ANOMALY_REPORT.md | New |
| 2 | SOURCE_RECONCILIATION_REPORT.md | New |
| 3 | TEST_SET_GOVERNANCE_REPORT.md | New |
| 4 | LEGACY_ARTIFACT_AUDIT_REPORT.md | New |
| 5 | TEMPORAL_DISTRIBUTION_SHIFT_REPORT.md | New |
| 6 | TEMPORAL_PROXY_RISK_REPORT.md | New |
| 7 | FEATURE_2_1_HOTFIX_REPORT.md | New |
| 8 | HOTFIX_CHANGELOG.md | New |
| 9 | DATA_INTAKE_VALIDATION_REPORT.md | Regenerated |
| 10 | TEMPORAL_SPLIT_REPORT.md | Regenerated |
| 11 | FEATURE_2_1_VALIDATION_REPORT.md | Regenerated |
| 12 | FEATURE_2_1_COMPLETION_REPORT.md | Regenerated |

---

## 5. Final Decision

| Criterion | Status |
|---|---|
| All hard gates | **PASS** |
| Contract deviations resolved | PASS (exception registered) |
| Source reconciled | PASS (Parquet = CSV) |
| Split verified independently | PASS (C1 correct, C2/C3 fixed) |
| Test governance documented | PASS |
| Legacy artifacts quarantined | PASS |
| Temporal risks classified | PASS (HIGH) |
| Validation depth adequate | PASS (93 content checks) |

### Overall: **PASS_WITH_WARNINGS**

Feature 2.1 is eligible for closure. Feature 2.2 may begin.
