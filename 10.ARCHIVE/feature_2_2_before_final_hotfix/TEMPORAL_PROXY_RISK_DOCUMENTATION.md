# TEMPORAL PROXY RISK DOCUMENTATION

**Feature 2.2 — Leakage-Safe Preprocessing Pipeline**
**Document Type**: Risk Assessment
**Generated**: 2026-07-17

---

## 1. Executive Summary

This document identifies and quantifies temporal proxy risks in the Feature 2.2 preprocessing pipeline. Three primary temporal proxies were identified:

| Proxy | Risk Level | Missing % (Train) | Mitigation |
|---|---|---|---|
| release_month_missing | **HIGH** | 30.54% | Ablation study required |
| tempo_missing | LOW | 0.04% | Train-only median imputation |
| time_signature_missing | LOW | 0.04% | Train-only mode imputation |

---

## 2. release_month_missing — HIGH RISK

### 2.1 Quantification

| Split | release_month NULL | Total Rows | Missing % |
|---|---|---|---|
| Train (1900-2004) | 126,895 | 415,524 | **30.54%** |
| Val (2005-2013) | 8,455 | 85,272 | 9.92% |
| Test (2014-2021) | 1,139 | 85,876 | **1.33%** |

### 2.2 Why This Is a Temporal Proxy

The missingness pattern is **inversely correlated with time**:
- Older releases (train) → more likely to have missing release_month
- Newer releases (test) → less likely to have missing release_month

This creates a **leakage pathway**: if the model learns that `release_month_missing=1` predicts higher popularity, it may be learning temporal trends rather than true song characteristics.

### 2.3 Ablation Study Required

The following variants must be evaluated in Feature 2.3:

| Variant | Description | Expected Outcome |
|---|---|---|
| ABL-A | release_month + indicator | Baseline with proxy |
| B | release_month as 0 + indicator | Tests indicator utility |
| C | Drop release_month entirely | Tests if proxy harms more than helps |
| D | Decade from release_year | Proxy replacement |
| E | release_month + NO indicator | Removes proxy signal |

---

## 3. tempo_missing — LOW RISK

### 3.1 Quantification

| Split | tempo NULL | Total Rows | Missing % |
|---|---|---|---|
| Train | 154 | 415,524 | 0.04% |
| Val | 34 | 85,272 | 0.04% |
| Test | 140 | 85,876 | 0.16% |

### 3.2 Risk Assessment

- **Temporal correlation**: Minimal (similar rates across splits)
- **Imputation**: Train-only median (114.995) — verified in fitted_statistics.json
- **Missing indicator**: tempo_missing column added during fit
- **Risk level**: LOW

---

## 4. time_signature_missing — LOW RISK

### 4.1 Quantification

| Split | time_signature NULL | Total Rows | Missing % |
|---|---|---|---|
| Train | 160 | 415,524 | 0.04% |
| Val | 36 | 85,272 | 0.04% |
| Test | 141 | 85,876 | 0.16% |

### 4.2 Risk Assessment

- **Temporal correlation**: Minimal (similar rates across splits)
- **Imputation**: Train-only mode (4) — verified in fitted_statistics.json
- **Missing indicator**: NOT added (risk is LOW, not needed)
- **Risk level**: LOW

---

## 5. Mitigation Strategy

### 5.1 Immediate (Feature 2.2)

1. **Document** all temporal proxies in preprocessing manifest
2. **Enable** ablation study infrastructure (ABL-A through ABL-E)
3. **Log** indicator usage in experiment tracking

### 5.2 Evaluation (Feature 2.3)

1. **Run** ablation variants
2. **Compare** validation metrics across variants
3. **Select** optimal strategy based on validation performance
4. **Report** proxy impact on test set

### 5.3 Long-term (Feature 2.5)

1. **Report** final selected strategy
2. **Document** temporal shift impact on proxy effectiveness

---

## 6. Governance

| Item | Status |
|---|---|
| Documented in release_month_strategy.json | DONE |
| Ablation variants defined | DONE |
| Missing indicators added during fit (not transform) | VERIFIED |
| Train-only statistics enforced | VERIFIED |

---

**Risk Assessment Complete**
