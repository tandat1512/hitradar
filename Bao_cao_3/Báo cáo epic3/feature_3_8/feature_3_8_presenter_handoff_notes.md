# Presenter Handoff Notes

These notes use role placeholders until human assignment is confirmed.

| From → To | Short transition |
|---|---|
| Introduction → Dataset | “Tiếp theo, phần dữ liệu và cách chia tập sẽ do [DATASET_PRESENTER] trình bày.” |
| Dataset → Model | “Từ dữ liệu đã khóa, [MODEL_PRESENTER] sẽ trình bày cách nhóm chọn và đánh giá mô hình.” |
| Model → SHAP | “Sau kết quả dự đoán, [SHAP_PRESENTER] sẽ giải thích cách nhóm quan sát hành vi của model.” |
| SHAP → Architecture | “Tiếp theo, [ARCHITECTURE_PRESENTER] sẽ nối model với kiến trúc API và giao diện.” |
| Architecture → Demo | “Bây giờ [PRIMARY_DEMO_OPERATOR] sẽ thực hiện flow demo đã chuẩn bị.” |
| Demo → Limitations | “Sau demo, [LIMITATIONS_PRESENTER] sẽ chốt các giới hạn và cách sử dụng phù hợp.” |
| Limitations → Conclusion | “Cuối cùng, [CONCLUSION_PRESENTER] sẽ tổng kết và mời hội đồng đặt câu hỏi.” |

## Failure handoff

If live API fails, the current speaker pauses and says the exact disclosure from `DEMO_SCRIPT_FEATURE_3_8.md`; `[PRIMARY_DEMO_OPERATOR]` or `[BACKUP_DEMO_OPERATOR]` then follows the failure tree. No presenter should call precomputed evidence live inference.

**Status:** `COMPLETE_AS_TEMPLATE`; actual-name substitution is `PENDING_HUMAN_ASSIGNMENT`.
