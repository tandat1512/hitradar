# Feature 3.8 — Rehearsal Coordination Report

**Phase:** 4/5 · **Tasks:** 3.8.8–3.8.10 · **Người thực hiện:** Minh  
**Status:** `WAITING_FOR_HUMAN_REHEARSAL` · **Next phase:** `BLOCKED`

## Kết quả chuẩn bị

- Xác minh được contributor Minh (EPIC 3) và Đạt (EPIC 1/data), nhưng không có full team roster hoặc role acceptance.
- Tạo assignment/Q&A ownership template; tất cả presenter/operator/backup vẫn `UNASSIGNED`.
- Tạo handoff notes bằng role placeholders.
- Tạo rehearsal protocol bao phủ deck, handoffs, demo, failure drill, MUST_KNOW Q&A, section/total timing và issue capture.
- Tạo R1/R2 evidence forms với status `HUMAN_REHEARSAL_REQUIRED`; không tái sử dụng technical dry-run làm rehearsal.
- Tạo issue schema, pre-rehearsal risk list, timing/retest/comparison artifacts và readiness placeholder.

## Known pre-rehearsal risks

| Risk | Severity | Status |
|---|---|---|
| Roles chưa được human-confirm | BLOCKER | PENDING |
| `/explain` timeout 300s lịch sử | HIGH | RESOLVED_BY_FINAL_SMOKE; giữ skip rule |
| Screenshot/video và automatic offline UI chưa sẵn sàng | HIGH | PENDING |
| Dataset story/slide conflict | HIGH | RESOLVED_BY_PHASE_5_HOTFIX; legacy docs còn warning |

Đây là known risks trước rehearsal, không phải issue quan sát từ R1. Vì chưa có R1 thật, registry không tạo ID `F38-R1-*` giả.

## Human actions required

1. Xác nhận full roster và ký assignment/operator/Q&A ownership.
2. Ghi deck version/hash và chạy R1 đầy đủ theo protocol.
3. Điền actual section/demo/Q&A timing và answer quality.
4. Ghi issue `F38-R1-001...` từ evidence thực tế; sửa presentation-only issues.
5. Chạy R2 trên material mới, retest mọi BLOCKER/HIGH và weak Q&A.

## Scope safety

Không production code, model, schema hay dataset nào được sửa. Nếu rehearsal phát hiện product bug, phải đăng ký `PRODUCT_DEFECT_DISCOVERED_DURING_REHEARSAL` và tách hotfix khỏi Phase 3.8.

## Structural validation

5 test files kiểm tra assignment placeholders/names, protocol coverage, issue schema và retest matrix. Automated tests không đánh giá chất lượng human rehearsal.
