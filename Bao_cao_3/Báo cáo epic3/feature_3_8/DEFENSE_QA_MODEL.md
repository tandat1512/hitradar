# Defense Q&A — Model, Metrics and Selection

### Q M01 [BASIC] [MUST_KNOW]: Đây là regression hay classification?

**Short answer:** Đây là **regression** vì output là một điểm popularity liên tục 0–100. Project có thể phân tích bucket sau dự đoán, nhưng model chính không dự đoán class “hit/non-hit”.

**Detailed answer:** API trả `prediction_raw`, `prediction_clipped` và display integer; không trả probability hay class label.

**Project evidence:** `models/prediction.py`; `champion_test_metrics.json`.

**Common trap:** Gọi score là xác suất hit hoặc dùng accuracy classification.

**Safe wording:** “Continuous regression estimate on a 0–100 target.”

**Follow-up questions:** Vì sao không classification? Clipping có ảnh hưởng metric không?

### Q M02 [TRAP] [MUST_KNOW]: Target có ý nghĩa gì?

**Short answer:** Target là Spotify `target_popularity` 0–100 tại snapshot dữ liệu. Nó là platform proxy, không phải chất lượng nghệ thuật, xác suất thành hit hay thành công thương mại chắc chắn.

**Detailed answer:** Streams gần đây, playlist exposure, marketing, artist fame và time bias có thể ảnh hưởng target nhưng không nằm đầy đủ trong input.

**Project evidence:** `popularity_limitations.md`; `ML_READY_DATASET_VALIDATION_REPORT.md`.

**Common trap:** “100 nghĩa là chắc chắn hit.”

**Safe wording:** “Estimated historical Spotify popularity proxy.”

**Follow-up questions:** Popularity được Spotify tính chính xác thế nào? Snapshot date là khi nào?

### Q M03 [INTERMEDIATE] [MUST_KNOW]: Nhóm đã thử model nào?

**Short answer:** Final comparison machine-readable có XGBoost, Random Forest và Ridge; registry cũng có Dummy và Linear baselines. Deep learning không nằm trong evaluated candidate registry.

**Detailed answer:** Ba family chính được so sánh bằng expanding-window temporal CV và validation; test chưa được dùng khi chọn champion.

**Project evidence:** `model_comparison.json`; `experiment_registry.json`; `TEMPORAL_CV_REPORT.md`.

**Common trap:** Kể thêm SVM/neural network không có run evidence.

**Safe wording:** “Evaluated families recorded by the registry were XGBoost, Random Forest, Ridge, plus Dummy/Linear baselines.”

**Follow-up questions:** Candidate nào runner-up? Có statistical significance không?

### Q M04 [INTERMEDIATE] [MUST_KNOW]: Model cuối là gì và tại sao chọn?

**Short answer:** Champion là **XGBoost `EXP24-XGB-FINAL-001` v1.0.0**. Trong setup dự án, nó có CV RMSE 12.8624 và validation RMSE 15.2521, thấp hơn sát Random Forest 12.9201/15.3225, đồng thời fit time được ghi 17,2 giây so với 447,7 giây.

**Detailed answer:** Validation MAE/R² của XGBoost là 11.9015/0.0954, cũng nhỉnh hơn RF 11.9446/0.0871. Champion được lock trước khi mở test metrics.

**Project evidence:** `7.ML/7.7.model_training/metrics/model_comparison.json`; `champion_lock_manifest.json`.

**Common trap:** “XGBoost vượt trội rất xa” hoặc dùng test để giải thích selection.

**Safe wording:** “Best recorded CV/validation trade-off, with a small margin over Random Forest.”

**Follow-up questions:** Margin nhỏ có ổn định không? Vì sao fit time khác lớn?

### Q M05 [BASIC] [MUST_KNOW]: Kết quả test chính là gì?

**Short answer:** Trên 85.876 test rows: **MAE 17.65**, **RMSE 21.01**, **R² 0.0696**. Đây là metric regression và cho thấy performance còn hạn chế.

**Detailed answer:** Median absolute error là 16.29; underprediction rate 67.82%. Không chuyển các số này thành “accuracy”.

**Project evidence:** `champion_test_metrics.json`; `residual_bias_summary.json`.

**Common trap:** Suy diễn phần variance chưa giải thích thành tỷ lệ dự đoán đúng.

**Safe wording:** “Test regression metrics, not classification accuracy.”

**Follow-up questions:** Metric validation là bao nhiêu? Error theo năm thế nào?

### Q M06 [BASIC] [MUST_KNOW]: MAE nghĩa là gì?

**Short answer:** MAE là trung bình độ lớn sai số tuyệt đối giữa prediction và target. MAE 17.65 nghĩa là trên test set, độ lệch tuyệt đối trung bình khoảng 17,65 popularity points.

**Detailed answer:** Nó dễ giải thích theo đơn vị target nhưng không cho biết hướng sai và không mô tả tail error riêng.

**Project evidence:** `champion_test_metrics.json`.

**Common trap:** Nói mọi prediction đều sai đúng 17,65 điểm.

**Safe wording:** “Average absolute test error, not a per-song guarantee.”

**Follow-up questions:** Median AE khác gì? Có weighted MAE không?

### Q M07 [BASIC] [MUST_KNOW]: RMSE nghĩa là gì?

**Short answer:** RMSE lấy căn của trung bình squared error nên phạt lỗi lớn mạnh hơn MAE. RMSE test 21.01 cao hơn MAE 17.65 cho thấy large errors có ảnh hưởng đáng kể.

**Detailed answer:** RMSE dùng cho model selection trong temporal CV, nhưng phải đọc cùng MAE, residual và slice metrics.

**Project evidence:** `champion_test_metrics.json`; `model_comparison.json`.

**Common trap:** Gọi RMSE là phần trăm lỗi.

**Safe wording:** “Popularity-point error metric with stronger penalty for large misses.”

**Follow-up questions:** Vì sao chọn RMSE làm criterion? Có outlier sensitivity không?

### Q M08 [TRAP] [MUST_KNOW]: R² nghĩa là gì, có phải accuracy không?

**Short answer:** Không. **R² không phải accuracy.** R² so sánh khả năng giải thích variation của model với baseline dự đoán mean; test R² 0.0696 nghĩa là model chỉ giải thích khoảng 7% variance trong setup này.

**Detailed answer:** R² thấp phù hợp với việc audio features không nắm được nhiều yếu tố xã hội/thị trường. Nó không phải 7% prediction accuracy và không phải probability.

**Project evidence:** `champion_test_metrics.json`; `TECHNICAL_APPENDIX.md` metric interpretation.

**Common trap:** Biến hệ số R² thành một tỷ lệ đúng/sai của từng prediction.

**Safe wording:** “Coefficient of determination; not accuracy.”

**Follow-up questions:** R² âm có thể xảy ra không? Baseline mean là gì?

### Q M09 [TRAP] [MUST_KNOW]: Tại sao không dùng accuracy?

**Short answer:** Accuracy cần nhãn rời rạc và khái niệm đúng/sai; model này dự đoán số liên tục. Vì vậy nhóm dùng MAE, RMSE và R², rồi phân tích residual/slices.

**Detailed answer:** Nếu chuyển thành classification, phải định nghĩa threshold “hit” và sẽ thành một bài toán khác với loss/imbalance khác.

**Project evidence:** API response schema; metric contract and `champion_test_metrics.json`.

**Common trap:** Tự bucket target rồi báo accuracy như metric champion.

**Safe wording:** “Regression requires distance-based and variance metrics.”

**Follow-up questions:** Có threshold analysis phụ không?

### Q M10 [DEEP] [MUST_KNOW]: Model có overfit không?

**Short answer:** Evidence không cho phép khẳng định “không overfit”. XGBoost train RMSE 11.279, validation 15.252 và test 21.013; gap cùng temporal degradation là warning cần thừa nhận.

**Detailed answer:** Temporal CV, validation và locked test giúp đo rủi ro; regularization/subsampling có trong config. Nhưng performance giảm ở later period có thể gồm overfitting, distribution shift và target drift; project chưa tách nguyên nhân conclusively.

**Project evidence:** `experiment_registry.json`; `validation_test_comparison.json`.

**Common trap:** “Có CV nên chắc chắn không overfit.”

**Safe wording:** “We evaluated overfitting risk; evidence still shows a material generalization gap.”

**Follow-up questions:** Gap bao nhiêu? Learning curve có không?

### Q M11 [DEEP] [SHOULD_KNOW]: Validation và test khác nhau thế nào?

**Short answer:** Validation RMSE là 15.2521, test RMSE 21.0134; tăng 5.7613 điểm hay 37.77%, artifact gắn `LARGE_DEGRADATION`. Điều này phù hợp với temporal shift và là limitation quan trọng.

**Detailed answer:** Test period 2014–2021 muộn hơn validation 2005–2013. Không được quay lại tune trên test để xóa gap vì sẽ làm mất tính held-out.

**Project evidence:** `validation_test_comparison.json`; `split_manifest.json`.

**Common trap:** Chỉ báo validation đẹp và bỏ test.

**Safe wording:** “Later held-out performance is materially worse and is reported honestly.”

**Follow-up questions:** Có retrain bằng validation không? Drift monitoring thế nào?

### Q M12 [INTERMEDIATE] [MUST_KNOW]: Có feature selection không?

**Short answer:** Có. Train-only temporal CV chọn 13 engineered features bổ sung 18 baseline để tạo 31 selected features; combined experiment báo RMSE improvement 1.09% so với baseline trong setup selection.

**Detailed answer:** Nhóm gồm time, duration và audio interactions. Selection không dùng test và feature set được lock.

**Project evidence:** `FEATURE_SELECTION_REPORT.md`; `feature_selection_results.json`.

**Common trap:** Nói từng engineered feature đều vượt threshold; report cho thấy nhiều feature chỉ có giá trị trong combined set.

**Safe wording:** “Combined train-only ablation supported the locked 31-feature set.”

**Follow-up questions:** Feature nào selected? Vì sao giữ time feature?

### Q M13 [DEEP] [SHOULD_KNOW]: Vì sao 31 selected features thành 49 cột?

**Short answer:** 31 là semantic selected features; preprocessing như one-hot encoding làm một categorical feature thành nhiều model columns, nên estimator nhận matrix 49 cột. SHAP mapping nối 49 transformed columns về tên feature.

**Detailed answer:** Đây không phải 49 input fields người dùng. API vẫn nhận 18 raw fields và pipeline tự transform.

**Project evidence:** `selected_features.json`; `feature_names.json`; `shap_feature_mapping_validation.json`.

**Common trap:** Đồng nhất raw, selected và transformed dimension.

**Safe wording:** “18 raw → 31 semantic selected → 49 transformed estimator columns.”

**Follow-up questions:** One-hot columns cụ thể? SHAP aggregate ra sao?

### Q M14 [INTERMEDIATE] [SHOULD_KNOW]: Hyperparameter tuning được làm thế nào?

**Short answer:** Search budget ghi 12 config cho mỗi Ridge, Random Forest và XGBoost, chọn top 2 trước external validation. XGBoost dùng 3-fold expanding-window CV và final config có depth 7, learning rate 0.03, 454 estimators cùng regularization/subsampling.

**Detailed answer:** Screening dùng early stopping trên fold validation; final locked model ghi `early_stopping_used=false` và rounds cố định 454 sau selection.

**Project evidence:** `SEARCH_BUDGET_REPORT.md`; `xgboost_top2_selection.json`; `experiment_registry.json`.

**Common trap:** Gọi đây là exhaustive tuning hoặc nói test dùng trong tuning.

**Safe wording:** “Budgeted temporal-CV search, not exhaustive optimization.”

**Follow-up questions:** Vì sao 12 configs? Seed/reproducibility thế nào?

### Q M15 [TRAP] [MUST_KNOW]: Tại sao không dùng deep learning?

**Short answer:** Deep learning không có evaluated run trong project registry, nên em không nói nó đã thua. Scope hiện tại tập trung vào structured tabular features và so sánh linear/tree ensembles; muốn kết luận về deep learning cần một experiment công bằng riêng.

**Detailed answer:** XGBoost phù hợp với tabular baseline và có SHAP TreeExplainer support, nhưng đó là rationale kỹ thuật, không phải bằng chứng DL không thể tốt hơn.

**Project evidence:** `experiment_registry.json`; `model_comparison.json`.

**Common trap:** “Deep learning luôn tệ cho tabular data” hoặc “thiếu GPU” khi project không ghi.

**Safe wording:** “Not evaluated within the project scope; no comparative claim.”

**Follow-up questions:** Nếu thử DL sẽ dùng architecture nào? Evaluation budget?

### Q M16 [TRAP] [MUST_KNOW]: Prediction có bảo đảm bài hát sẽ hit không?

**Short answer:** Không. Nó là estimate của model trên historical platform target; MAE khoảng 17.65 và R² thấp cho thấy uncertainty lớn.

**Detailed answer:** Output không phải probability, causal forecast hay quyết định thương mại. UI clip score về 0–100 để hiển thị nhưng raw model uncertainty vẫn tồn tại.

**Project evidence:** `champion_test_metrics.json`; frontend `6_Limitations.py`.

**Common trap:** “Điểm trên 70 chắc chắn hit.”

**Safe wording:** “Model estimate, not a guarantee.”

**Follow-up questions:** Có prediction interval không? Threshold hit định nghĩa ở đâu?

### Q M17 [INTERMEDIATE] [SHOULD_KNOW]: Model được đóng gói thế nào?

**Short answer:** Package gồm full inference pipeline, schemas, examples và metadata; model ID/version được khóa. Runtime nhận 18-field payload và chạy cùng preprocessing/feature engineering đã đóng gói, không refit.

**Detailed answer:** Artifact manifest có hashes; model artifact chính trong package là `full_inference_pipeline.joblib`. Có discrepancy package version metadata 2.7.0 và runtime example 1.0.0, nên phải phân biệt model version với package version.

**Project evidence:** `artifact_manifest.json`; `model_version.json`; `package_version.json`.

**Common trap:** Nói model version và package version là một khi sources đang lệch.

**Safe wording:** “Model version is 1.0.0; exact package-version reporting requires reconciliation.”

**Follow-up questions:** Hash dùng làm gì? Có rollback/versioning không?

### Q M18 [TRAP] [MUST_KNOW]: Backend load và serve model ra sao?

**Short answer:** FastAPI load pipeline eager lúc startup qua `PipelineLoader`; frontend Streamlit gọi HTTP, không load model trực tiếp. Runtime inference không gọi fit/refit.

**Detailed answer:** `/health` báo `model_loaded`; `/predict`, `/explain`, `/what-if` chạy ở backend. Tách lớp giúp một inference contract, validation tập trung và tránh duplicate model/SHAP logic trong UI.

**Project evidence:** `api.py`; `pipeline_loader.py`; `TECHNICAL_APPENDIX.md`.

**Common trap:** “Streamlit tự chạy model” hoặc “FastAPI làm model chính xác hơn.”

**Safe wording:** “FastAPI owns inference; Streamlit owns interaction and rendering.”

**Follow-up questions:** Nếu nhiều worker thì model load mấy lần? Có authentication/rate limit không?
