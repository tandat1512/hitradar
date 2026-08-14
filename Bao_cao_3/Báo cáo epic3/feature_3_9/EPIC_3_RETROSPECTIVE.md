# EPIC 3 RETROSPECTIVE

## Productization, Integration & Defense

### 1. Tổng quan Epic 3

Epic 3 dự kiến chuyển các artifact ML đã khóa thành một sản phẩm demo có FastAPI, Streamlit, dashboard, kiểm thử tích hợp, tài liệu vận hành, gói bảo vệ và quy trình bàn giao cuối. Mục tiêu không chỉ là có code chạy, mà còn phải có repository/release tái lập được, tài liệu nhất quán và bằng chứng demo–bảo vệ.

### 2. Phạm vi đã thực hiện

| Feature | Kết quả lịch sử |
|---|---|
| 3.1 Artifact Intake & Validation | PASS_WITH_WARNINGS / CLOSED_WITH_WARNINGS |
| 3.2 FastAPI Backend | PASS_WITH_WARNINGS / ELIGIBLE_FOR_CLOSURE |
| 3.3 Streamlit Frontend | PASS / ELIGIBLE_FOR_CLOSURE |
| 3.4 Dashboard & Visualization | PASS_WITH_WARNINGS / ELIGIBLE_FOR_CLOSURE |
| 3.5 Integration & E2E | FAIL / NOT_CLOSED |
| 3.6 Performance, Reliability & Demo Backup | FAIL / NOT_CLOSED |
| 3.7 Documentation & User Guide | PASS_WITH_WARNINGS / ELIGIBLE_FOR_CLOSURE |
| 3.8 Defense Preparation | WAITING_FOR_HUMAN_ACTION / NOT_CLOSED |
| 3.9 Final Delivery | FAIL / NOT_CLOSED |

### 3. Những gì đã làm tốt

- Feature 3.1 và audit 3.9 xác minh model, schemas, dataset và SHAP bằng hash; final audit vẫn ghi nhận 0 artifact thiếu và 0 hash mismatch.
- Backend và frontend giữ ranh giới HTTP: frontend không load model hay tính SHAP trực tiếp; các endpoint và OpenAPI được tài liệu hóa nhất quán.
- Dashboard dùng dữ liệu local read-only và có kiểm tra phạm vi; trang được đưa vào luồng demo bảy bước.
- Feature 3.8 xây dựng demo script, Q&A dataset/model/SHAP/limitations và cách diễn đạt non-causal, không biến R² thành accuracy.
- Phase 2 của Feature 3.9 đã sửa drift tài liệu về 586.672 dòng, 1900–2021, Python defense 3.13.14 và broken links; claim/API/metric mismatch sau hotfix bằng 0.
- Các Gate giữ trạng thái trung thực: smoke không bị gọi là demo, rehearsal không bị gọi là defense, và không có commit/submission/grade giả.

### 4. Những gì chưa tốt

- Version-control baseline bị để quá muộn: working tree cuối vẫn có hàng trăm file untracked và commit hiện tại không tái lập được Epic 3.
- Feature 3.5 và 3.6 lịch sử chưa có live E2E/clean-clone/benchmark/startup/offline acceptance đầy đủ nên vẫn NOT_CLOSED.
- Fact registry chưa được dùng làm nguồn duy nhất từ đầu, dẫn tới tài liệu và UI giữ các số dataset legacy khác nhau.
- Gói bảo vệ không có deck thật, phân công presenter/operator, rehearsal, backup media và physical checks.
- Release/submission/event workflow được chuẩn bị nhưng không có final SHA, receipt, demo evidence hoặc defense outcome.

### 5. Những lỗi/khó khăn đáng chú ý

| Issue | Feature | Impact | Resolution |
|---|---|---|---|
| Thiếu live E2E và fresh-clone acceptance | 3.5 | Không thể đóng integration | Vẫn OPEN; cần chạy lại trong môi trường sạch |
| Thiếu benchmark/startup/offline/backup acceptance | 3.6 | Không thể xác nhận reliability cuối | Vẫn OPEN |
| run_all không truyền child environment đã dựng | 3.6/3.9 | Override port/artifact có thể sai | Workaround đã ghi docs; code fix vẫn OPEN |
| Dataset fact drift 169.681/1922–2019 | 3.7/3.8/3.9 | Docs/UI mâu thuẫn | Docs đã hotfix; UI Limitations vẫn OPEN |
| Final slide deck 0-byte/missing | 3.8/3.9 | Không audit/nộp/bảo vệ được | OPEN — cần deck thật và visual review |
| Local/remote SHA không đồng nhất | 3.9 | Push không an toàn | OPEN — fetch/reconcile có phê duyệt |

### 6. Những gì nhóm học được

#### ML productization
Artifact chỉ đáng tin khi model, preprocessing, schema và metadata được kiểm tra cùng nhau bằng hash và contract.

#### API design
OpenAPI và Pydantic tạo ranh giới rõ giữa input 18 trường, response và lỗi 422/503; SHAP/What-if cần disclaimer non-causal ngay trong contract.

#### Frontend/backend integration
Giữ frontend chỉ gọi HTTP giúp tránh hai implementation inference khác nhau, nhưng startup/env propagation phải được test bằng port override thật.

#### Testing
Source review không thay thế live E2E, fresh clone và acceptance. Test readiness phải được phép fail khi deliverable thật còn thiếu.

#### Performance
Không được công bố p50/p95 khi Feature 3.6 vẫn PENDING; benchmark phải giữ cùng environment và input contract.

#### Documentation
Fact registry cần được tạo sớm và tự động kiểm tra xuyên README, report, UI, Q&A và slide.

#### Demo reliability
Precomputed offline evidence phải được gắn nhãn, có UI/media thật và không được mô tả như live inference.

#### Presentation/defense
Outline/Q&A không thay cho deck, phân công, rehearsal, backup và event evidence của con người.

### 7. Những quyết định kỹ thuật đúng

- Khóa champion model và không retrain/tune/refit trong Epic 3.
- Tách FastAPI/Streamlit và giữ inference ở backend.
- Dùng temporal metrics, công bố MAE/RMSE/R² thấp một cách trung thực.
- Dùng manifest/hash cho model, dataset và SHAP.
- Chọn `FINAL_COMMIT_ONLY` khi repository không có tag convention thay vì tự invent semantic tag.

### 8. Những quyết định có thể làm tốt hơn

- Commit theo từng feature và CI trên fresh clone thay vì gom hàng trăm untracked files cuối Epic.
- Chạy integration/performance acceptance ngay khi Feature 3.5/3.6 được tạo.
- Đưa fact registry vào test của UI/doc từ đầu.
- Chỉ viết “final” sau khi có actual deck/release SHA/human approval.

### 9. Technical Debt còn lại

- Startup child environment propagation defect.
- Dirty/untracked production baseline và remote reconciliation.
- Clean-install, live E2E, startup/offline/benchmark acceptance chưa hoàn tất.
- UI Limitations còn dataset year legacy.
- Final slide, roles, rehearsals, backup media và physical checks còn thiếu.
- Submission requirements/receipt, demo/defense evidence và reviewer approval chưa có.

### 10. Nếu làm lại từ đầu

1. Tạo branch/commit baseline và CI ngay Feature 3.1.
2. Sinh OpenAPI, fact registry và docs checks từ canonical artifacts.
3. Dùng một clean environment job cho backend/frontend/startup/E2E mỗi phase.
4. Chuẩn bị deck, presenter roles và backup media song song với product work.
5. Định nghĩa submission/release convention trước Feature 3.9.

### 11. Hướng phát triển tiếp theo

Đây là FUTURE WORK: cải thiện model/generalization, bổ sung CI/CD, auth/rate limiting/TLS, production telemetry, automated deck fact extraction và release automation sau khi baseline hiện tại được đóng sạch.

### 12. Kết quả Epic 3

**INCOMPLETE.** Nhiều component và tài liệu đã được xây dựng, nhưng Feature 3.5, 3.6, 3.8 và 3.9 chưa đóng; repository/release/submission/demo/defense vẫn chưa hoàn tất. Retrospective hoàn thành không thay đổi các Gate lịch sử này.
