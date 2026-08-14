# Defense Q&A — SHAP and What-If

### Q S01 [BASIC] [MUST_KNOW]: SHAP là gì?

**Short answer:** SHAP là phương pháp attribution dùng để giải thích cách các feature đóng góp vào prediction của model. Trong project, nó giải thích hành vi XGBoost với input cụ thể, không chứng minh quan hệ nhân quả ngoài đời thực.

**Detailed answer:** Ý tưởng cộng base value với các contribution để tái tạo output trong model output space.

**Project evidence:** `shap_explainer_manifest.json`; `shap_additivity_validation.json`.

**Common trap:** “SHAP tìm ra nguyên nhân bài hát nổi tiếng.”

**Safe wording:** “Feature contributions to the model prediction.”

**Follow-up questions:** SHAP dựa trên game theory thế nào? Assumptions là gì?

### Q S02 [BASIC] [MUST_KNOW]: Tại sao dùng SHAP?

**Short answer:** Vì project cần giải thích prediction local và có thể kiểm tra additivity thay vì chỉ đưa một score. Với tree model, project có artifact TreeExplainer và mapping feature đã validate.

**Detailed answer:** SHAP cung cấp direction/magnitude theo model, hỗ trợ debugging và communication; nó không làm prediction chính xác hơn.

**Project evidence:** `feature_3_1_shap_asset_validation.json`.

**Common trap:** “Dùng SHAP để tăng accuracy.”

**Safe wording:** “Interpretability layer, not a performance booster.”

**Follow-up questions:** Vì sao không permutation importance/LIME?

### Q S03 [INTERMEDIATE] [MUST_KNOW]: SHAP giải thích cái gì?

**Short answer:** Nó giải thích output của đúng model, đúng pipeline và đúng input đang xét. Nó không giải thích toàn bộ thị trường âm nhạc hay nguyên nhân xã hội tạo popularity.

**Detailed answer:** `/explain` dự đoán cùng input, transform thành matrix rồi tính contribution; UI chọn top feature theo absolute magnitude.

**Project evidence:** `5.UNG_DUNG/5.1.backend_api/api.py` `/explain`.

**Common trap:** Chuyển model explanation thành domain truth.

**Safe wording:** “How this model arrived at this output.”

**Follow-up questions:** Nếu model sai thì explanation có hữu ích không?

### Q S04 [BASIC] [MUST_KNOW]: SHAP value dương/âm nghĩa là gì?

**Short answer:** Dương nghĩa là feature contribution đẩy model output cao hơn base value; âm nghĩa là kéo thấp hơn, với input và representation đó. Dấu không nói feature gây ra outcome thực tế.

**Detailed answer:** Magnitude dùng để rank contribution local; correlated/transformed features có thể chia attribution.

**Project evidence:** Explain UI wording; `shap_value_validation.json`.

**Common trap:** “Dương nghĩa là tăng feature sẽ luôn tăng popularity.”

**Safe wording:** “Pushes the model output up/down relative to its base.”

**Follow-up questions:** Zero contribution nghĩa gì? Scale SHAP là gì?

### Q S05 [INTERMEDIATE] [SHOULD_KNOW]: Base value là gì?

**Short answer:** Base value là expected model output dùng làm điểm xuất phát của SHAP; prediction xấp xỉ base cộng tổng SHAP values. API expose `base_value` trong ExplainResponse.

**Detailed answer:** Project validate additivity trong raw output space; base không phải popularity trung bình toàn thị trường và không phải threshold hit.

**Project evidence:** `models/prediction.py`; `shap_additivity_validation.json`.

**Common trap:** Gọi base value là ground truth hoặc dataset target mean mà không kiểm tra.

**Safe wording:** “Explainer reference output.”

**Follow-up questions:** Base được tính trên background nào?

### Q S06 [INTERMEDIATE] [MUST_KNOW]: Local và global SHAP khác nhau thế nào?

**Short answer:** Local SHAP giải thích một prediction; global SHAP tổng hợp magnitude/pattern trên nhiều sample để nhìn model behavior rộng hơn. Project có `/explain` cho local và global asset 5.000×49.

**Detailed answer:** Global importance vẫn là model-level association, không phải causal importance hay universal ranking.

**Project evidence:** `shap_value_validation.json`; global SHAP figures.

**Common trap:** Dùng global ranking để kết luận mọi bài hát.

**Safe wording:** “Aggregated model attribution over the analyzed sample.”

**Follow-up questions:** Global sample được chọn thế nào?

### Q S07 [DEEP] [SHOULD_KNOW]: Project dùng explainer nào?

**Short answer:** Artifact ghi **SHAP TreeExplainer**, phù hợp với XGBoost tree model. Đây là project fact có manifest, không phải suy đoán.

**Detailed answer:** Cần tách hai implementation. Epic 2 explainability artifact dùng background train-only 1.000×49. FastAPI live hiện tại trong `api.py` lại xây `shap.TreeExplainer(model)` chỉ từ champion estimator, không truyền background artifact vào constructor.

**Project evidence:** `shap_explainer_manifest.json`; `api.py:_build_shap_explainer`.

**Common trap:** Gọi KernelExplainer hoặc DeepExplainer.

**Safe wording:** “TreeExplainer, as recorded by the explainer manifest.”

**Follow-up questions:** Feature perturbation mode nào? Model output space nào?

### Q S08 [DEEP] [SHOULD_KNOW]: Background data là gì?

**Short answer:** Validated background transformed có shape **1.000×49**, source train-only; raw background có 1.000×18. Validation/test overlap đều 0.

**Detailed answer:** Background tạo reference distribution cho explainer. Train-only source tránh dùng test distribution để xây explanation artifact.

**Project evidence:** `feature_3_1_shap_asset_validation.json`; `shap_train_source_validation.json`.

**Common trap:** Nói background là toàn dataset hoặc 5.000 rows; 5.000 là global SHAP sample.

**Safe wording:** “1,000 train-only background rows; 5,000 rows for global SHAP values.”

**Follow-up questions:** Sampling method có stratified không?

### Q S09 [DEEP] [MUST_KNOW]: Có kiểm tra additivity không?

**Short answer:** Có. Trên 5.000 sample, 5.000/5.000 nằm trong tolerance 0.001; max absolute reconstruction error khoảng `6.75e-05`, status PASS.

**Detailed answer:** Check dùng estimator raw output: base cộng SHAP xấp xỉ prediction. Nó kiểm tra numerical consistency, không kiểm tra causal correctness.

**Project evidence:** `shap_additivity_validation.json`.

**Common trap:** “Additivity pass chứng minh explanation đúng về mặt nguyên nhân.”

**Safe wording:** “Numerically reconstructs the model output within tolerance.”

**Follow-up questions:** Vì sao có sai số nhỏ? Tolerance chọn thế nào?

### Q S10 [INTERMEDIATE] [SHOULD_KNOW]: Explain endpoint chạy flow gì?

**Short answer:** `POST /explain` nhận cùng 18-field request, chạy prediction, transform qua feature engineering/preprocessing, tính SHAP trên estimator, map tên và trả top 5 theo absolute value cùng toàn bộ shap map.

**Detailed answer:** Response có prediction, base value, SHAP values, top features, model ID/version. Prediction phải nhất quán với `/predict` cho cùng input.

**Project evidence:** `api.py`; `models/prediction.py`.

**Common trap:** Nói frontend đọc file global SHAP để giả local explanation.

**Safe wording:** “Backend computes a fresh local model attribution for the request.”

**Follow-up questions:** Latency thế nào? Có cache explainer không?

### Q S11 [TRAP] [MUST_KNOW]: SHAP tính ở đâu và vì sao frontend không tính?

**Short answer:** SHAP tính ở FastAPI backend; Streamlit chỉ gửi request và render response. Thiết kế này giữ model/pipeline/SHAP logic ở một nơi và tránh frontend truy cập artifact trực tiếp.

**Detailed answer:** Nó cải thiện contract consistency và giảm duplication; không tự động biến hệ thống thành production-secure.

**Project evidence:** `api.py`; frontend `2_Explain.py`; `TECHNICAL_APPENDIX.md`.

**Common trap:** “Frontend tính SHAP cho nhanh.”

**Safe wording:** “Backend owns inference and explanation; frontend owns presentation.”

**Follow-up questions:** Nếu backend scale nhiều worker thì cache ra sao?

### Q S12 [TRAP] [MUST_KNOW]: SHAP có chứng minh feature làm bài hát nổi tiếng không?

**Short answer:** Không. SHAP chỉ cho biết model phân bổ contribution như thế nào dưới dữ liệu và representation đã học; correlation/model behavior không phải causation.

**Detailed answer:** Confounding, omitted variables, time bias và correlated features vẫn tồn tại. Muốn causal claim cần thiết kế nghiên cứu can thiệp và assumptions riêng.

**Project evidence:** frontend `6_Limitations.py`; `USER_MANUAL.md` SHAP warning.

**Common trap:** “Energy là nguyên nhân làm popularity tăng.”

**Safe wording:** “The model associates this input with a contribution; no real-world causal claim.”

**Follow-up questions:** Muốn kiểm causal phải làm gì?

### Q S13 [DEEP] [SHOULD_KNOW]: Limitation của SHAP là gì?

**Short answer:** SHAP giải thích model, nên model/data bias đi vào explanation; correlated/transformed features có thể làm attribution khó đọc. Kết quả cũng phụ thuộc background và output space.

**Detailed answer:** Additivity chỉ đảm bảo reconstruction; không đảm bảo model đúng, feature độc lập hay explanation ổn định ngoài distribution.

**Project evidence:** SHAP manifests; project Limitations page.

**Common trap:** “SHAP là lời giải thích khách quan tuyệt đối.”

**Safe wording:** “Faithful to the configured model computation within tested tolerance, not necessarily to reality.”

**Follow-up questions:** Có stability analysis không? Correlation xử lý thế nào?

### Q S14 [TRAP] [MUST_KNOW]: Nếu SHAP unavailable thì sao?

**Short answer:** Demo recovery rule là skip nhanh và nói rõ unavailable; offline mode đánh dấu Explain `NOT_AVAILABLE`. Không dùng số SHAP tự tạo hoặc precomputed không được validate cho input đó.

**Detailed answer:** Phase 2 dry-run ngày 2026-08-11 từng timeout 300 giây, nhưng final technical smoke ngày 2026-08-12 đã trả Explain thành công trong khoảng 400 ms. Skip rule vẫn giữ như recovery plan; không còn gọi timeout cũ là trạng thái runtime hiện tại.

**Project evidence:** `feature_3_8_demo_dry_run.json`; Feature 3.6 offline contract.

**Common trap:** Hiển thị ảnh/số dự phòng rồi gọi là live.

**Safe wording:** “Explain did not respond in time; this step is skipped and no live SHAP result is claimed.”

**Follow-up questions:** Vì sao timeout? Có optimize được không?

### Q S15 [TRAP] [MUST_KNOW]: What-if có phải causal inference không?

**Short answer:** Không. What-if chỉ thay một hoặc nhiều input, chạy lại cùng model và so sánh hai predictions; delta là model-output difference.

**Detailed answer:** Backend tạo `after_dict`, predict before/after rồi tính delta. Phase 2 dry-run tăng energy từ 0.793 lên 0.95 nhưng prediction giảm, cho thấy không được dùng intuition để nói trước hướng.

**Project evidence:** `api.py:/what-if`; `feature_3_8_demo_dry_run.json`.

**Common trap:** “Nếu nghệ sĩ tăng energy thì popularity thật sẽ giảm 2,38.”

**Safe wording:** “The model responds this way under the modified input; no real-world effect is established.”

**Follow-up questions:** Input combination có realistic không? Có enforce constraints giữa features không?
