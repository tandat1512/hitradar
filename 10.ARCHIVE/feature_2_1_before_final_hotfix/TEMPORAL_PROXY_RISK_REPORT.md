# TEMPORAL PROXY RISK REPORT

**Feature 2.1 HOTFIX — HitRadar Pro EPIC 2**

---

## 1. Risk Statement

`release_month` missing rate is highly correlated with time period:
- Train (1900–2004): **30.54%** NULL
- Validation (2005–2013): **9.92%** NULL
- Test (2014–2021): **1.33%** NULL

If Feature 2.2 creates a binary `release_month_missing` indicator, this feature will effectively encode "is this track from the older catalog?" — a temporal proxy that leaks information about which split a track belongs to.

---

## 2. Why This Is NOT Direct Target Leakage

- `release_month_missing` does not directly reveal `target_popularity`
- It is derived from an input feature (`release_month`), not the target
- It reflects a genuine data quality pattern — older Spotify entries have less complete metadata

---

## 3. Why This IS Still a Risk

| Concern | Explanation |
|---|---|
| **Temporal proxy** | The model could learn "metadata completeness" instead of audio patterns |
| **Split discrimination** | A model with this feature could partially identify which split a row belongs to |
| **Inflated train performance** | If the model learns "old catalog = low popularity" via this proxy |
| **Generalization risk** | Future data (post-2021) will have ~0% missing release_month, making this feature useless |
| **Confounded with release_year** | Already have `release_year` as a direct temporal signal |

---

## 4. Related Features with Similar Risk

| Feature | Risk Type |
|---|---|
| `release_month_missing` (if created) | Strong temporal proxy |
| `release_year` | Direct time signal — intentional, documented |
| `decade` | Derived from release_year — intentional |
| `release_precision` | Partially correlated with era — moderate proxy |
| `tempo` NULL indicator (if created) | Very weak — only 328 NULL total, 0 in val/test |
| `time_signature` NULL indicator (if created) | Very weak — only 337 NULL total, 0 in val/test |

---

## 5. Required Ablation Experiments (Feature 2.2/2.3)

Feature 2.1 does NOT decide the preprocessing strategy. Feature 2.2/2.3 MUST run ablation experiments:

| Ablation ID | Configuration | Purpose |
|---|---|---|
| **ABL-A** | Include `release_month_missing` indicator | Baseline with proxy |
| **ABL-B** | Exclude `release_month_missing` indicator | Compare without proxy |
| **ABL-C** | Include `release_year`, exclude missing indicator | Time signal without proxy |
| **ABL-D** | Exclude `release_year` AND missing indicator | No temporal features |
| **ABL-E** | Include/exclude `release_precision` | Test precision as proxy |

### Evaluation Criteria for Ablation

1. Compare validation MAE/RMSE between variants
2. Check if model performance on test degrades more for ABL-A (proxy overfitting)
3. Analyze feature importance — if `release_month_missing` ranks high, it confirms proxy behavior
4. Per-decade error analysis — if model errors are uncorrelated with era in ABL-D, temporal proxies are not needed

---

## 6. Recommendation

**Do NOT make a final decision in Feature 2.1.** Document the risk and carry forward.

If forced to choose a default:
- **Safe default**: ABL-C — include `release_year` (explicit temporal signal), do NOT create `release_month_missing` indicator
- **Rationale**: `release_year` already captures temporal information explicitly; adding a proxy for metadata completeness adds noise without clear predictive value

---

## 7. Carry-Forward

| Owner | Action |
|---|---|
| Feature 2.2 | Implement ablation variants ABL-A through ABL-E |
| Feature 2.3 | Run feature importance analysis with/without temporal proxies |
| Feature 2.5 | Report per-decade and per-bucket metrics for selected variant |
