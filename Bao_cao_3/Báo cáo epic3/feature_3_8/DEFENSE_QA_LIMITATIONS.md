# Defense Q&A — Limitations, Architecture and Scope

### Q L01 [TRAP] [MUST_KNOW]: Hạn chế lớn nhất của dự án là gì?

**Short answer:** Lớn nhất là target/data chỉ là historical Spotify proxy trong khi nhiều driver của popularity không nằm trong 18 input; vì vậy generalization yếu. Test R² chỉ 0.0696 và RMSE tăng 37.77% từ validation sang later test.

**Detailed answer:** Đây vừa là data/target limitation vừa là model limitation; không thể sửa chỉ bằng đổi thuật toán.

**Project evidence:** `popularity_limitations.md`; `champion_test_metrics.json`; `validation_test_comparison.json`.

**Common trap:** “Project không có hạn chế đáng kể.”

**Safe wording:** “Useful research prototype with substantial data and generalization limits.”

**Follow-up questions:** Top 3 limitations? Mitigation hiện tại?

### Q L02 [BASIC] [MUST_KNOW]: Dataset limitation là gì?

**Short answer:** Historical, platform-specific, không chứng minh geographic/genre representativeness và không có evidence sau 2021. Narrative docs còn lệch scope với locked pipeline, nên cần reconciliation.

**Detailed answer:** Train chỉ đến 2004; later periods dùng validation/test. Platform time bias và missing contextual drivers giới hạn áp dụng.

**Project evidence:** `split_manifest.json`; `feature_3_8_qa_source_registry.json`.

**Common trap:** “586 nghìn dòng nên chắc chắn đại diện.”

**Safe wording:** “Large does not mean representative.”

**Follow-up questions:** Bias nào đã đo? Có sampling weights không?

### Q L03 [TRAP] [MUST_KNOW]: Target limitation là gì?

**Short answer:** Spotify popularity 0–100 không phải chất lượng âm nhạc, hit probability hay doanh thu. Nó phụ thuộc platform activity, recency, playlist và yếu tố ngoài audio.

**Detailed answer:** Vì target là proxy, ngay cả prediction khớp target cũng không chứng minh thành công ngoài Spotify hoặc tương lai.

**Project evidence:** `popularity_limitations.md`.

**Common trap:** Gọi target là “độ hay” hoặc “thành công thật”.

**Safe wording:** “Platform popularity proxy at a historical snapshot.”

**Follow-up questions:** Có target tốt hơn không?

### Q L04 [BASIC] [MUST_KNOW]: Model limitation là gì?

**Short answer:** Test MAE 17.65, RMSE 21.01 và R² 0.0696 cho thấy sai số lớn và explanatory power thấp. Underprediction xảy ra ở 67.82% test cases.

**Detailed answer:** Đây là aggregate metrics; một số slice/năm tệ hơn. Không được dùng score cho quyết định critical/commercial.

**Project evidence:** `champion_test_metrics.json`; `residual_bias_summary.json`.

**Common trap:** Chỉ nêu model ID mà bỏ performance yếu.

**Safe wording:** “Limited predictive utility; estimate only.”

**Follow-up questions:** Error lớn nhất? Bias calibration?

### Q L05 [DEEP] [MUST_KNOW]: Generalization ngoài distribution thế nào?

**Short answer:** Project không bảo đảm OOD generalization. Later test đã giảm mạnh so với validation; temporal robustness là `MODERATELY_VARIABLE` và yearly RMSE tăng theo year với correlation 0.9303 trong artifact.

**Detailed answer:** Input validation chỉ bảo đảm schema/range, không bảo đảm sample thuộc training distribution.

**Project evidence:** `temporal_robustness_summary.json`; `validation_test_comparison.json`.

**Common trap:** “Pydantic accept thì model chắc chắn reliable.”

**Safe wording:** “Schema-valid does not imply in-distribution or reliable.”

**Follow-up questions:** Có drift detector/OOD detector không?

### Q L06 [TRAP] [MUST_KNOW]: SHAP limitation là gì?

**Short answer:** SHAP giải thích model, không giải thích nguyên nhân thực tế; nó kế thừa bias/sai số của model và phụ thuộc background/feature representation. Additivity pass không biến attribution thành causal truth.

**Detailed answer:** Correlated features và one-hot mapping cũng có thể làm contribution khó diễn giải.

**Project evidence:** `shap_additivity_validation.json`; Limitations page.

**Common trap:** “SHAP chứng minh feature quan trọng thật.”

**Safe wording:** “Model attribution, not causal evidence.”

**Follow-up questions:** Stability/correlation audit?

### Q L07 [TRAP] [MUST_KNOW]: What-if limitation là gì?

**Short answer:** What-if chỉ chạy lại model với input sửa; không kiểm tra can thiệp đó khả thi về âm nhạc hay causal effect. Delta cũng chịu mọi bias và OOD risk của model.

**Detailed answer:** UI validate từng field range nhưng chưa chứng minh joint combination realistic.

**Project evidence:** `api.py:/what-if`; frontend `6_Limitations.py`.

**Common trap:** Dùng delta làm hướng dẫn sản xuất nhạc.

**Safe wording:** “Hypothetical model response only.”

**Follow-up questions:** Có constraint giữa energy/loudness không?

### Q L08 [INTERMEDIATE] [SHOULD_KNOW]: Dashboard limitation là gì?

**Short answer:** Music Trends đọc local CSV và mô tả dataset hiện có; không cần backend nhưng cần frontend và file ở cùng filesystem. Nó không đại diện global industry và narrative scope đang lệch current file.

**Detailed answer:** Current technical parse là 586.672 rows, 1900–2021. Story/slide Feature 3.8 đã reconcile; số 169.681/1922–2019 chỉ còn trong một số legacy documentation và không được dùng để mô tả UI hiện tại.

**Project evidence:** frontend `4_Trends.py`; Phase 2 dry-run.

**Common trap:** “Dashboard là real-time Spotify analytics.”

**Safe wording:** “Read-only descriptive local-data dashboard.”

**Follow-up questions:** Deploy tách service thì sao?

### Q L09 [INTERMEDIATE] [MUST_KNOW]: Performance limitation là gì?

**Short answer:** Historical benchmark cho warm inference khoảng 15,6 ms trong một local environment, nhưng không phải SLA. `/explain` từng timeout 300 giây ở Phase 2 dry-run, sau đó PASS khoảng 400 ms trong final smoke; cả hai chỉ là quan sát cục bộ.

**Detailed answer:** Benchmark phụ thuộc máy, version và workload; project chưa có production load test/concurrency SLA.

**Project evidence:** `feature_3_1_benchmark_results.json`; `feature_3_8_demo_dry_run.json`.

**Common trap:** “API luôn phản hồi dưới 16 ms.”

**Safe wording:** “Local benchmark, not a production guarantee.”

**Follow-up questions:** Explain bottleneck? Concurrent users?

### Q L10 [TRAP] [MUST_KNOW]: Model này production-ready chưa?

**Short answer:** Chưa. Đây là local academic prototype; chưa có security hardening, auth/rate limiting, distributed cache, production observability, SLA hay validated deployment scale.

**Detailed answer:** Functional architecture và contracts có, nhưng production readiness cần review riêng về security, privacy, operations, drift và rollback.

**Project evidence:** `TECHNICAL_APPENDIX.md` deployment/security scope; Limitations page.

**Common trap:** “Có FastAPI nên production-ready.”

**Safe wording:** “Demo/research ready within tested scope, not production ready.”

**Follow-up questions:** Checklist production hóa?

### Q L11 [INTERMEDIATE] [SHOULD_KNOW]: Local deployment limitation là gì?

**Short answer:** Backend và frontend chạy local trên ports 8000/8501; Trends cần local files. Không có evidence cho multi-node deployment, shared session state hay high availability.

**Detailed answer:** Streamlit state theo session và cache per process; nhiều worker có thể load model/explainer riêng.

**Project evidence:** `TECHNICAL_APPENDIX.md`; run scripts.

**Common trap:** “Có thể scale ngang ngay không cần đổi.”

**Safe wording:** “Single-host local architecture in the validated scope.”

**Follow-up questions:** Containerization? Redis? Load balancer?

### Q L12 [TRAP] [MUST_KNOW]: Offline demo limitation là gì?

**Short answer:** Offline chỉ được dùng canonical precomputed Predict và static/local evidence; Explain/What-if `NOT_AVAILABLE`. Feature 3.6 chưa validate offline UI implementation và backup screenshots/video cũng chưa sẵn sàng.

**Detailed answer:** Khi fallback phải nói nguyên văn rằng không thực hiện live inference; tuyệt đối không gọi precomputed result là live.

**Project evidence:** Feature 3.6 offline contract/final audit; Phase 2 backup matrix.

**Common trap:** “Offline app vẫn inference như thường.”

**Safe wording:** “Explicitly disclosed precomputed evidence, not live inference.”

**Follow-up questions:** Nếu cần offline Explain thì làm sao validate?

### Q L13 [TRAP] [MUST_KNOW]: Nếu model dự đoán sai thì sao?

**Short answer:** Sai số là expected risk đã đo, không phải exception hiếm; output chỉ là decision-support/demo estimate. Người dùng phải xem metric, limitations và không ra quyết định critical từ một prediction.

**Detailed answer:** Với ground truth sau này, có thể log/evaluate drift dưới governance; không tự động retrain trong runtime.

**Project evidence:** test metrics; frontend Limitations page; no-refit contract.

**Common trap:** “Model không sai vì đã test.”

**Safe wording:** “Measured error exists; human judgment remains required.”

**Follow-up questions:** Feedback loop? Monitoring target delay?

### Q L14 [TRAP] [MUST_KNOW]: Nếu API chết thì sao?

**Short answer:** UI phải báo backend unavailable; demo check health một lần, retry nhanh một lần rồi chuyển fallback có disclosure. Predict offline chỉ dùng canonical precomputed evidence; Explain/What-if bỏ qua.

**Detailed answer:** Không retry vô hạn và không giấu failure bằng fake response. Trends/Limitations có thể tiếp tục nếu local file/UI còn chạy.

**Project evidence:** Phase 2 failure tree; Feature 3.6 runbook/offline contract.

**Common trap:** Gọi fallback result là live.

**Safe wording:** “API unavailable; switching to disclosed precomputed mode, no live inference.”

**Follow-up questions:** Health/recovery endpoint? Circuit breaker?

### Q L15 [TRAP] [MUST_KNOW]: Tại sao cần FastAPI khi Streamlit có thể load model?

**Short answer:** FastAPI tạo một inference contract dùng chung, tập trung validation/model/SHAP logic và giữ frontend không truy cập artifact. Nó hỗ trợ testability và separation of concerns; không phải vì Streamlit về kỹ thuật không thể load model.

**Detailed answer:** `/predict`, `/explain`, `/what-if` nhất quán model version và request schema. Trade-off là thêm network/process dependency.

**Project evidence:** `api.py`; frontend API client; `TECHNICAL_APPENDIX.md`.

**Common trap:** “Streamlit không thể chạy Python model.”

**Safe wording:** “Architectural separation and a single backend contract.”

**Follow-up questions:** Monolith có đơn giản hơn cho demo không?

### Q L16 [INTERMEDIATE] [MUST_KNOW]: Nếu có thêm thời gian, cải thiện gì trước?

**Short answer:** Ưu tiên: hoàn tất reconcile các legacy docs; theo dõi độ ổn định Explain qua nhiều lần chạy; thu thập dữ liệu mới và context leakage-safe; đánh giá drift/calibration/OOD; sau đó harden deployment và tạo backup media thật. Model mới phải có version mới và giữ test governance.

**Detailed answer:** Không nên chỉ tune thêm trên locked test. Improvement phải tách data quality, predictive performance, explanation reliability và operations.

**Project evidence:** top limitations; Phase 2 warnings; model/test lock artifacts.

**Common trap:** “Chỉ cần deep learning là giải quyết hết.”

**Safe wording:** “Fix evidence lineage and reliability first, then run governed model improvements.”

**Follow-up questions:** Roadmap 1 tuần/1 tháng? Success criteria?

### Q L17 [DEEP] [BACKUP]: Nếu không biết câu trả lời thì nói thế nào?

**Short answer:** “Trong phạm vi dự án, nhóm chưa đánh giá riêng yếu tố đó nên em không muốn khẳng định quá mức. Evidence hiện tại cho thấy …”. Sau đó nêu source gần nhất và cách kiểm chứng.

**Detailed answer:** Ví dụ license, geographic mix, causal effect, production concurrency và nguyên nhân của lần Explain timeout lịch sử chưa được project chứng minh conclusively.

**Project evidence:** `feature_3_8_qa_source_registry.json` source policy.

**Common trap:** Dùng kiến thức chung thành project fact hoặc trả lời chắc chắn để tránh nói “chưa biết”.

**Safe wording:** “Project evidence does not establish this conclusively.”

**Follow-up questions:** Em sẽ thiết kế experiment/audit nào để trả lời?
