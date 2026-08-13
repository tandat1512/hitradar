# Feature 3.8 — Defense Q&A Report

**Phase:** 3/5 · **Tasks:** 3.8.4–3.8.7 · **Người thực hiện:** Minh  
**Date:** 2026-08-11 · **Decision:** `PASS_WITH_WARNINGS`

## Bank coverage

| Bank | Questions | Nội dung |
|---|---:|---|
| Dataset | 16 | origin, scope, quality, preprocessing, temporal split, leakage, representativeness |
| Model | 18 | regression, target, candidates, selection, metrics, overfitting, tuning, packaging, serving |
| SHAP | 15 | attribution, sign/base, local/global, TreeExplainer, additivity, endpoint, noncausal, What-if |
| Limitations | 17 | data/target/model/generalization, dashboard, runtime, local/offline, production, recovery |
| Rapid fire | 25 | 1–2 sentence answers for likely questions |

Tổng bank chính: **66 câu**. Mỗi câu có short answer, detailed answer, project evidence, common trap, safe wording và follow-up; đồng thời có difficulty/priority tag.

## Facts presenter phải khóa

- Locked ML data và story/slide Feature 3.8: **586.672 rows, 1900–2021**; một số legacy docs còn scope 169.681/1922–2019 và không phải nguồn canonical.
- Split: train **415.524** (1900–2004), validation **85.272** (2005–2013), test **85.876** (2014–2021).
- Dimensions: **18 raw → 31 selected → 49 transformed**.
- Champion: XGBoost `EXP24-XGB-FINAL-001`, model version `1.0.0`.
- Test: MAE **17.65**, RMSE **21.01**, R² **0.0696**; R² không phải accuracy.
- Validation-to-test RMSE degradation: **37.77%**; không khẳng định model không overfit.
- SHAP: TreeExplainer; background **1.000×49** train-only; global values **5.000×49**; additivity **5.000/5.000** pass tolerance 0.001.
- SHAP và What-if: model behavior, không causal.
- Project: local academic prototype, không production-ready.

## Model-selection defense

XGBoost được chọn vì machine-readable comparison ghi CV RMSE 12.8624 và validation RMSE 15.2521, nhỉnh hơn Random Forest 12.9201/15.3225; validation MAE/R² cũng nhỉnh hơn và recorded fit time thấp hơn. Bank không gọi khoảng cách này là vượt trội lớn và không dùng test metric để biện hộ cho quyết định champion.

## Unsupported policy

Các fact chưa có conclusive evidence—license/source URL chính xác, geographic distribution, deep-learning comparison, causal effect, production concurrency và root cause exact của Explain timeout—được trả lời bằng mẫu:

> “Trong phạm vi dự án, nhóm chưa đánh giá riêng yếu tố đó nên em không muốn khẳng định quá mức. Evidence hiện tại cho thấy …”

## Consistency warnings

1. Dataset scope trong README/Manual/Technical Appendix lệch locked split/training source. Q&A giữ warning, không tự bịa filtering lineage.
2. Package version metadata/runtime example lệch; Q&A chỉ khóa model version.
3. Offline UI implementation chưa được validate; fallback được gọi đúng là evidence-only/precomputed.
4. `/explain` từng timeout 300 giây ở Phase 2 dry-run nhưng PASS khoảng 400 ms trong final smoke; Q&A vẫn hướng dẫn skip khi không phản hồi nhanh và không dùng fabricated SHAP.

## Claim audit và tests

| Check | Result |
|---|---:|
| Q&A internal fact mismatches | 0 |
| R² mislabeled as accuracy | 0 |
| Guarantee claims | 0 |
| Causal SHAP claims | 0 |
| Causal What-if claims | 0 |
| Unsupported claims | 0 |
| Production-ready overclaims | 0 |
| Pytest | 8 passed, 0 failed, 0 errors |

JUnit: `pytest_feature_3_8_phase_3.xml`.
