# TEST SET GOVERNANCE REPORT

**Feature 2.1 HOTFIX — HitRadar Pro EPIC 2**

---

## 1. Test Set Definition

| Property | Value |
|---|---|
| Split | Test |
| Years | 2014–2021 |
| Rows | 85,876 |
| Ratio | 14.64% |
| ID file | `7.ML/7.4.splits/test_ids.parquet` |
| Lock file | `7.ML/7.4.splits/test_set_lock.json` |

---

## 2. Test Set Usage Classification

### A. Pre-Lock Descriptive Audit (Feature 2.1) — PERMITTED

During Feature 2.1 data intake, test labels (`target_popularity`) were read for the following descriptive purposes:

- Row count verification
- Target distribution profiling (mean, median, std, buckets)
- Missing value counts
- Temporal shift assessment (PSI, KS statistics)
- Year range verification

**No model was trained.** No model metric was computed. No model was selected using test data.

### B. Model-Selection Usage (Feature 2.2–2.4) — PROHIBITED

During Feature 2.2 (preprocessing), 2.3 (feature engineering), and 2.4 (model training/tuning):
- `y_test` must NOT be read
- Test set features may be transformed using train-fitted preprocessors
- No model performance metrics may be computed on test
- No feature selection decisions may use test data

### C. Final Test Evaluation (Feature 2.5) — PERMITTED (ONE TIME)

After model is locked and all hyperparameters are fixed:
- Compute final metrics on test set exactly once
- Record results in `test_set_lock.json` under `model_metrics_on_test`
- Update `final_evaluation_status` from `NOT_STARTED` to `COMPLETED`

---

## 3. Lock Mechanism

### test_set_lock.json Fields

| Field | Value | Purpose |
|---|---|---|
| status | locked | Lock state |
| data_version | ml-ready-2026-07-16-v1 | Tied to data snapshot |
| split_version | temporal-split-v1 | Tied to split config |
| test_ids_hash | (SHA-256) | Verify test IDs unchanged |
| test_row_count | 85,876 | Verify row count |
| lock_timestamp | (ISO 8601) | When lock was created |
| lock_owner | Feature 2.1 | Who locked |
| permitted_stage | Feature 2.5 | When test eval allowed |
| prohibited_actions | 5 items | What is forbidden |
| descriptive_audit_performed | true | Pre-lock audit done |
| descriptive_audit_fields | 4 categories | What was audited |
| final_evaluation_status | NOT_STARTED | No model eval yet |
| model_metrics_on_test | null | No metrics yet |

### Guard Script

`9.SCRIPTS/validate_test_set_lock.py` checks:

1. Lock file exists and parses
2. All required governance keys present
3. Lock status is "locked"
4. data_version matches `data_version.json`
5. split_version matches `split_version.txt`
6. test_ids_hash matches `test_ids.parquet`
7. test_row_count matches `test_ids.parquet`
8. No test metric files exist before Feature 2.5
9. No Feature 2.2–2.4 scripts reference `y_test`
10. Descriptive audit properly documented
11. Final evaluation not started
12. No model metrics on test

---

## 4. Corrected Language

### Previous (INCORRECT)
> "Test set chưa từng được mở."

### Corrected
> "Test labels were read during Feature 2.1 pre-lock descriptive audit for data quality documentation. No model-based test misuse was detected. No model was trained, selected, or evaluated using test data."

---

## 5. Carry-Forward to Feature 2.2–2.4

Feature 2.2–2.4 scripts MUST NOT:
- Import or read `target_popularity` for test split rows
- Compute any prediction metric on test split
- Use test data for feature selection or hyperparameter tuning
- Compare preprocessing variants using test performance

Feature 2.2–2.4 scripts MAY:
- Transform test features using train-fitted preprocessors
- Count test rows for pipeline verification
- Verify test IDs match lock

---

## 6. Evidence Files

| File | Purpose |
|---|---|
| `7.ML/7.4.splits/test_set_lock.json` | Lock state and governance |
| `9.SCRIPTS/validate_test_set_lock.py` | Guard validation script |
