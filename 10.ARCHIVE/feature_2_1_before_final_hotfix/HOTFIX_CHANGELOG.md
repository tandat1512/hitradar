# HOTFIX CHANGELOG

**Feature 2.1 — HitRadar Pro EPIC 2**

---

## Hotfix Version: 1.0
**Date**: 2026-07-16
**Status**: APPLIED

---

### BUG-001: Candidate Split Zero Counts Identical (CONFIRMED)

**Previous report**: All 3 candidates (C1, C2, C3) showed identical zero counts:
- Train zero = 35,952
- Validation zero = 3,144
- Test zero = 5,594

**Actual values (independently recomputed)**:

| Candidate | Train Zero | Val Zero | Test Zero | Sum |
|---|---:|---:|---:|---:|
| C1 | 35,952 | 3,144 | 5,594 | 44,690 |
| C2 | 35,918 | 3,178 | 5,594 | 44,690 |
| C3 | 35,824 | 2,567 | 6,299 | 44,690 |

**Root cause**: Original script reused split DataFrames across candidates without re-filtering. C1 values were computed first and carried over.

**Impact**: The selected candidate C1 values happen to be correct. C2 and C3 statistics were wrong in the original TEMPORAL_SPLIT_REPORT. The candidate selection decision is unaffected because C1 was selected on ratio score, not zero counts.

**Fix**: 
- Created `split_candidate_diagnostics.csv` with independently computed statistics
- Regenerated `TEMPORAL_SPLIT_REPORT.md` with correct values
- Regenerated `FEATURE_2_1_COMPLETION_REPORT.md`

---

### BUG-002: Year 1900 Not Flagged as Contract Deviation (CONFIRMED)

**Previous report**: Stated "Không có contract deviation" despite year 1900 being outside the EPIC 1 documented range of 1921–2021.

**Root cause**: Validation script had no year range check. Profiling reported min_year=1900 but did not cross-reference against EPIC 1 documentation.

**Fix**:
- Created `RELEASE_YEAR_ANOMALY_REPORT.md`
- Created `data_exceptions.json` with formal exception registry
- Added year range validation with exception support

---

### BUG-003: test_set_lock.json Missing Governance Fields

**Previous content**: Only contained `status`, `test_ids_hash`, `test_row_count`, `lock_timestamp`.

**Fix**: Upgraded to include `data_version`, `split_version`, `permitted_stage`, `prohibited_actions`, `descriptive_audit_performed`, `descriptive_audit_fields`, `descriptive_audit_note`, `final_evaluation_status`, `model_metrics_on_test`, `lock_owner`.

---

### BUG-004: Incorrect Language "Test chưa từng được mở"

**Previous report**: Stated test set was never opened, which is false — test labels were read for descriptive audit.

**Fix**: Corrected to "Test labels were read during Feature 2.1 pre-lock descriptive audit. No model-based test misuse detected."

---

### BUG-005: Legacy .pkl Files Not Quarantined

**Previous**: 3 empty .pkl files in `4.MODELS/4.1.trained/` were noted as "pre-existing" and ignored.

**Fix**: Moved to `4.MODELS/legacy_epic1/` with `DO_NOT_USE.md` and `legacy_artifact_manifest.json`.

---

### BUG-006: Validation Only Checked File Existence

**Previous**: Many validation checks only verified if a file exists, not its content.

**Fix**: Rewrote `validate_feature_2_1.py` with 93 content-level checks including JSON/YAML parsing, key presence, hash verification, union/intersection, chronology, and manifest consistency.

---

### BUG-007: Temporal Shift Labeled "Expected Warning"

**Previous**: PSI = 0.87 (val) and 1.54 (test) dismissed as "expected warning."

**Fix**: Classified as HIGH severity. Created `TEMPORAL_DISTRIBUTION_SHIFT_REPORT.md` with PSI, KS test results, and risk classification.

---

### BUG-008: release_month_missing Temporal Proxy Not Documented

**Previous**: Not mentioned in any report.

**Fix**: Created `TEMPORAL_PROXY_RISK_REPORT.md` with ablation experiment requirements.

---

### BUG-009: "50/50 PASS" Claim Before Semantic Checks

**Previous**: Claimed 50/50 PASS when validation only checked existence.

**Fix**: Now 93 content-level checks, all PASS. Report accurately reflects check scope.
