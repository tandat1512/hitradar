# Feature 3.8 — Demo Script Report

**Task:** 3.8.2 · **Người thực hiện:** Minh · **Date:** 2026-08-11  
**Decision:** `PASS_WITH_WARNINGS` · **Primary:** `LIVE` · **Fallback:** `OFFLINE_PRECOMPUTED`  
**PRIMARY_OPERATOR:** `UNASSIGNED`

## Kết quả

Demo script đã được chuyển thành flow ngắn và kiểm soát được:

`PRECHECK → Home → Predict → Explain → What-if → Music Trends → Model Info / Limitations → End`

Script dùng canonical input của Feature 3.5/3.1, khóa hash input, mô tả hành động UI, lời presenter, expected visible state, endpoint, timing, failure action và skip rule cho từng bước. Predict là bước neo; Explain/What-if chỉ chạy khi live và có cùng baseline.

## Canonical scenario

- Source: `7.ML/7.10.model_packaging/package/examples/example_input.json`
- SHA-256: `19847ab49e692374203e0fadbdca17e7ca9ae680c1016d2a26dfde6730d33bc0`
- Model: `EXP24-XGB-FINAL-001`, version `1.0.0`
- Predict fixture: `46.421062 ± 0.001`, speaker đọc gọn “khoảng 46”
- What-if: `energy 0.793 → 0.95`
- Expected What-if: đọc live before/after/delta; không giả định hướng hoặc exact output trong script
- Offline: Predict precomputed only; Explain và What-if `NOT_AVAILABLE`

## Technical dry-run

Run được ghi đúng là `TECHNICAL_DRY_RUN`, không phải Rehearsal #1:

| Check | Kết quả |
|---|---|
| Backend health | PASS — healthy, model_loaded=true |
| Frontend health | PASS — HTTP 200, body `ok` |
| Predict | PASS — 46.421062, khớp fixture |
| What-if energy 0.95 | PASS — before 46.421062, after 44.045479, delta -2.375583 |
| Explain | PASS_FINAL_SMOKE — khoảng 400 ms; dry-run trước đó từng timeout 300 giây |
| Model Info | PASS — model/version đúng; `metrics=null` |
| Trends data source | PASS_DATA_SOURCE — 586.672 dòng hợp lệ, 1900–2021 |
| Model artifact hash | Unchanged — `7ff4b118...1a7d99` trước và sau |

Kết quả What-if âm chứng minh vì sao lời thoại không được mặc định “tăng energy thì điểm tăng”. Lần Explain timeout lịch sử vẫn được giữ như recovery trigger; final smoke đã PASS và không dùng fixture hoặc số SHAP tự tạo thay cho live evidence.

## Source conflicts đã xử lý

1. Gate cuối Feature 3.5/3.6 ngày 2026-08-07 vẫn ghi live evidence bị chặn. Report này giữ chúng là lịch sử nguồn và ghi dry-run hiện tại riêng, không sửa ngược trạng thái cũ.
2. Offline contract yêu cầu explicit mode nhưng closure Feature 3.6 nói UI implementation deferred. Vì vậy fallback là evidence-based, có disclosure bắt buộc, không tuyên bố tự động chuyển mode.
3. Story/slide Feature 3.8 đã đồng bộ với Trends ở 586.672 dòng, 1900–2021. Một số legacy docs còn 169.681/1922–2019; presenter không dùng các giá trị cũ cho UI hiện tại.
4. Screenshot count là 0; video là `MANUAL_RECORDING_REQUIRED`. Backup matrix ghi `MISSING`, không ghi available.

## Claim audit

| Claim type | Count |
|---|---:|
| Guarantee | 0 |
| Causal SHAP | 0 |
| Causal What-if | 0 |
| Offline represented as live | 0 |
| Unsupported metric | 0 |

## Test evidence

9 test files Phase 2: **9 passed, 0 failed, 0 errors**. JUnit: `pytest_feature_3_8_phase_2.xml`.

## Cảnh báo mang sang Phase 3/4

- Investigate hoặc chấp nhận skip `/explain` trước buổi bảo vệ; không để presenter chờ.
- Capture và validate screenshot/video thật trước khi đổi trạng thái backup media.
- Gán operator thật ở Phase 4; hiện vẫn `UNASSIGNED`.
- Nếu official duration được công bố, cập nhật timing plan và validate lại; hiện chỉ là planning estimate.
