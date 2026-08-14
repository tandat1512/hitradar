# Defense Q&A Master Index

Master này chỉ là index để tránh duplicate và giữ bốn bank độc lập dễ bảo trì.

| Bank | Scope | Questions | MUST_KNOW focus |
|---|---|---:|---|
| [DEFENSE_QA_DATASET.md](DEFENSE_QA_DATASET.md) | Origin, quality, preprocessing, split, leakage, representativeness | 16 | D03–D05, D08, D10–D12, D14–D15 |
| [DEFENSE_QA_MODEL.md](DEFENSE_QA_MODEL.md) | Regression, selection, metrics, overfitting, packaging, serving | 18 | M01–M05, M08–M12, M15–M16, M18 |
| [DEFENSE_QA_SHAP.md](DEFENSE_QA_SHAP.md) | SHAP concepts, assets, endpoint, noncausal policy, What-if | 15 | S01–S04, S06, S09, S11–S12, S14–S15 |
| [DEFENSE_QA_LIMITATIONS.md](DEFENSE_QA_LIMITATIONS.md) | Top limitations, production/offline/API/dashboard scope | 17 | L01–L07, L09–L10, L12–L16 |
| [DEFENSE_QA_RAPID_FIRE.md](DEFENSE_QA_RAPID_FIRE.md) | 25 probable questions, 1–2 sentence answers | 25 | Luyện phản xạ |

## Evidence policy

1. Dùng locked machine-readable artifacts trước narrative docs.
2. ML pipeline và story/slide Feature 3.8: 586.672 rows, 1900–2021. Một số legacy docs còn 169.681/1922–2019; không tự gán giá trị cũ thành subset.
3. R² không phải accuracy; prediction không phải probability/guarantee.
4. SHAP/What-if không causal.
5. Khi thiếu evidence: “Trong phạm vi dự án, nhóm chưa đánh giá riêng yếu tố đó nên em không muốn khẳng định quá mức. Evidence hiện tại cho thấy …”.
