# Defense Q&A — Dataset, Preprocessing and Leakage

Mỗi câu có thể trả lời phần **Short answer** trong 15–30 giây. Chỉ mở phần chi tiết khi hội đồng hỏi tiếp. Nguồn chuẩn cho pipeline ML là manifest/split đã khóa; README, User Manual và Technical Appendix đang có unresolved discrepancy về scope dataset.

### Q D01 [BASIC] [MUST_KNOW]: Dataset lấy từ đâu?

**Short answer:** Project dùng một dataset lịch sử được tài liệu mô tả là Spotify-derived. Evidence nội bộ xác nhận các file raw `tracks.csv`, `artists.csv` và `dict_artists.json`, nhưng không xác lập đầy đủ URL tải gốc hay license, nên em không khẳng định chi tiết đó.

**Detailed answer:** `tracks.csv` có audio features, metadata và track popularity; `artists.csv` có metadata nghệ sĩ. ML-ready view giữ 18 input, một ID và target.

**Project evidence:** `DATASET_AUDIT_REPORT.md`: tracks 586.672 dòng, artists 1.162.095 dòng; `ML_READY_DATASET_VALIDATION_REPORT.md`.

**Common trap:** Gọi dataset là toàn bộ Spotify hoặc tự nêu một Kaggle URL chưa có bằng chứng.

**Safe wording:** “Curated Spotify-derived historical dataset; exact upstream acquisition details are not conclusively established by current project evidence.”

**Follow-up questions:** License là gì? Snapshot được lấy ngày nào? Có market/geography nào?

### Q D02 [INTERMEDIATE] [SHOULD_KNOW]: Vì sao nhóm chọn dataset này?

**Short answer:** Evidence cho thấy dataset phù hợp để xây bài toán regression có cấu trúc: target 0–100 và các audio/metadata feature nhất quán. Tuy nhiên project không có artifact ghi một study so sánh nhiều dataset, nên em không nói đây là dataset tốt nhất.

**Detailed answer:** Ưu điểm là quy mô lớn, ID duy nhất, target không null và có dữ liệu theo thời gian. Nhược điểm là platform bias, historical bias và thiếu yếu tố marketing/artist context.

**Project evidence:** `ML_READY_DATASET_VALIDATION_REPORT.md`; `popularity_limitations.md`.

**Common trap:** “Chọn vì dataset hoàn hảo và đại diện toàn ngành.”

**Safe wording:** “Nó đủ phù hợp với scope nghiên cứu, không phải lựa chọn tối ưu đã được chứng minh.”

**Follow-up questions:** Đã benchmark dataset khác chưa? Có dữ liệu streaming mới hơn không?

### Q D03 [TRAP] [MUST_KNOW]: Dataset có bao nhiêu record và bao phủ năm nào?

**Short answer:** Pipeline split/training đã khóa dùng **586.672** record, từ **1900 đến 2021**. Một số narrative docs ghi 169.681 và 1922–2019; project chưa có evidence chứng minh đó là subset nào, nên Q&A kỹ thuật dùng manifest đã khóa và công khai discrepancy.

**Detailed answer:** Train 415.524 dòng (1900–2004), validation 85.272 (2005–2013), test 85.876 (2014–2021); tổng khớp 586.672.

**Project evidence:** `7.ML/7.4.splits/split_manifest.json`; `preprocessing_split_verification.json`.

**Common trap:** Trộn hai bộ số hoặc tự giải thích 169.681 là “sau lọc” khi chưa có lineage.

**Safe wording:** “Locked ML pipeline evidence: 586,672 rows, 1900–2021; narrative scope mismatch is pending reconciliation.”

**Follow-up questions:** Vì sao tài liệu lệch? Slide nào phải sửa? Có hash dataset không?

### Q D04 [BASIC] [MUST_KNOW]: Có bao nhiêu feature và target là gì?

**Short answer:** API nhận **18 input feature** audio và metadata. ML-ready view có 20 cột: `track_id`, 18 input và target `target_popularity`; target là điểm Spotify popularity từ 0 đến 100.

**Detailed answer:** Feature engineering thêm 13 feature để thành 31 selected features; preprocessing/encoding tạo ma trận 49 cột cho model. ID và target không đi vào input model.

**Project evidence:** `ML_READY_DATASET_VALIDATION_REPORT.md`; `selected_features.json`; `feature_names.json`.

**Common trap:** Nói 49 input người dùng hoặc gọi popularity là xác suất hit.

**Safe wording:** “18 raw inputs → 31 selected features → 49 model-matrix columns; target is a continuous platform score.”

**Follow-up questions:** 13 engineered features là gì? Vì sao 31 thành 49?

### Q D05 [INTERMEDIATE] [MUST_KNOW]: Dataset có missing value không?

**Short answer:** Có. ML-ready evidence ghi `release_month` thiếu 136.489, `tempo` thiếu 328 và `time_signature` thiếu 337; target và ID không thiếu.

**Detailed answer:** Missing không bị điền trước split. Preprocessing fit trên train: tempo dùng median 114.995, time signature dùng most-frequent 4.0, release month dùng category `__MISSING__`.

**Project evidence:** `ML_READY_DATASET_VALIDATION_REPORT.md`; `missing_value_strategy.json`.

**Common trap:** “Dataset sạch hoàn toàn, không có missing.”

**Safe wording:** “Missing exists and is handled by train-fitted or explicit strategies.”

**Follow-up questions:** Vì sao không drop? Median có phù hợp mọi thời kỳ không?

### Q D06 [BASIC] [SHOULD_KNOW]: Có duplicate không?

**Short answer:** Raw audit ghi 0 duplicate rows cho `tracks.csv` và `artists.csv`; ID của hai file là unique. Split verification cũng ghi 0 duplicate ID trong từng split và 0 overlap giữa các split.

**Detailed answer:** Điều đó hỗ trợ row identity và split integrity, nhưng không chứng minh không có hai bản thu nội dung giống nhau với ID khác.

**Project evidence:** `DATASET_AUDIT_REPORT.md`; `preprocessing_split_verification.json`.

**Common trap:** Suy từ unique ID ra “không có duplicate về mặt âm nhạc”.

**Safe wording:** “No duplicate rows/IDs were found under the project checks.”

**Follow-up questions:** Có kiểm tra duplicate theo tên/nghệ sĩ/audio fingerprint không?

### Q D07 [INTERMEDIATE] [SHOULD_KNOW]: Outlier và invalid value được xử lý thế nào?

**Short answer:** Audit phát hiện duration cực ngắn/dài, tempo bằng 0, time signature bằng 0 và loudness dương. Preprocessing contract dùng IQR clipping cho `duration_min`, `tempo`, `loudness`; các audio feature vốn bị giới hạn 0–1 được kiểm tra theo miền.

**Detailed answer:** Clipping threshold phải fit trên train để tránh leakage. Evidence không cho phép nói mọi outlier đã bị xóa; chiến lược chính là clip một số continuous fields và giữ audit warning.

**Project evidence:** `DATASET_AUDIT_REPORT.md`; `outlier_config.json`; `preprocessing_fit_audit.json`.

**Common trap:** “Nhóm xóa toàn bộ outlier.”

**Safe wording:** “Selected numeric outliers are clipped under a train-fitted contract; not every unusual record is deleted.”

**Follow-up questions:** Vì sao IQR 1.5? Có sensitivity analysis không?

### Q D08 [INTERMEDIATE] [MUST_KNOW]: Pipeline preprocessing tổng thể là gì?

**Short answer:** Nhóm split theo thời gian trước, rồi fit imputer, encoder và scaler trên train; validation/test chỉ transform. Sau đó feature engineering và preprocessing tạo input matrix cho model.

**Detailed answer:** Continuous fields dùng median imputation và StandardScaler trong pipeline P23-A/P22-A-like; categorical fields dùng most-frequent và OneHotEncoder `handle_unknown=ignore`; binary fields passthrough sau imputation.

**Project evidence:** `feature_engineering_pipeline.py:create_preprocessor`; `preprocessing_fit_audit.json`.

**Common trap:** Nói fit preprocessing trên toàn dataset.

**Safe wording:** “Split first; fit preprocessing on train only; transform later periods.”

**Follow-up questions:** Categorical columns nào? Unknown category được xử lý ra sao?

### Q D09 [DEEP] [SHOULD_KNOW]: Có scaling và encoding không, XGBoost có cần scaling không?

**Short answer:** Pipeline project có OneHotEncoder cho categorical fields và StandardScaler cho continuous fields. Tree model không phụ thuộc scaling như linear model, nhưng pipeline dùng preprocessing thống nhất giữa model candidates và đóng gói inference.

**Detailed answer:** `release_month`, `decade`, `release_precision`, `key`, `time_signature` thuộc categorical set; `explicit` và `mode` là binary. Em không khẳng định scaling làm XGBoost tốt hơn nếu project chưa có ablation riêng cho câu đó.

**Project evidence:** `encoding_config.json`; `scaling_config.json`; `feature_engineering_pipeline.py`.

**Common trap:** “XGBoost bắt buộc phải scale” hoặc “không hề scale.”

**Safe wording:** “Scaling is part of the shared packaged preprocessing; its isolated benefit to XGBoost was not established.”

**Follow-up questions:** One-hot làm tăng bao nhiêu cột? Vì sao không ordinal encode?

### Q D10 [INTERMEDIATE] [MUST_KNOW]: Train/validation/test split như thế nào?

**Short answer:** Split là temporal, không phải random: train 1900–2004, validation 2005–2013, test 2014–2021. Tỷ lệ lần lượt khoảng 70,83%, 14,53% và 14,64%.

**Detailed answer:** Test được khóa trước khi model selection; champion lock ghi model và feature set đã khóa trước khi mở test labels/metrics.

**Project evidence:** `split_manifest.json`; `champion_lock_manifest.json`.

**Common trap:** Nói stratified random split hoặc đã dùng test để chọn champion.

**Safe wording:** “Chronological split with a locked final test period.”

**Follow-up questions:** Vì sao mốc 2004/2013? Có temporal CV không?

### Q D11 [INTERMEDIATE] [MUST_KNOW]: Vì sao chọn temporal split?

**Short answer:** Vì mục tiêu gần với dự đoán cho giai đoạn sau từ dữ liệu trước đó và release year liên quan mạnh đến popularity. Temporal split kiểm tra shift thực tế hơn random mixing các thời kỳ.

**Detailed answer:** Train-only temporal CV dùng expanding windows ba fold trong giai đoạn 1900–2004. Nó không loại bỏ time bias, nhưng làm rủi ro đó nhìn thấy rõ hơn.

**Project evidence:** `data_leakage_risks.md`; `TEMPORAL_CV_REPORT.md`.

**Common trap:** “Temporal split giải quyết hoàn toàn data drift.”

**Safe wording:** “It reduces optimistic time mixing and exposes temporal degradation; it does not eliminate drift.”

**Follow-up questions:** Nếu random split thì metric có thể khác thế nào?

### Q D12 [TRAP] [MUST_KNOW]: Có data leakage không?

**Short answer:** Project có guardrails chống các leakage đã xác định: target/proxy columns bị loại, split trước preprocessing, mọi fit audit đều train-only, và split overlap bằng 0. Em chỉ nói các check này pass, không tuyên bố mọi dạng leakage có thể có đều không tồn tại.

**Detailed answer:** Artist popularity và target-derived aggregates không nằm trong baseline; test labels bị khóa trước champion selection. Time bias vẫn là limitation chứ không được gọi là đã giải quyết.

**Project evidence:** `data_leakage_risks.md`; `preprocessing_fit_audit.json`; `champion_lock_manifest.json`.

**Common trap:** “Không có bất kỳ leakage nào.”

**Safe wording:** “No leakage was found by the project’s defined guardrails; residual risks remain possible.”

**Follow-up questions:** Target encoding thì sao? Release year có phải leakage không?

### Q D13 [DEEP] [BACKUP]: Release year có phải leakage không?

**Short answer:** Không tự động là target leakage vì nó có thể biết tại thời điểm phát hành, nhưng nó mang time bias rất mạnh. Việc dùng nó phải phù hợp use case và được đánh giá theo temporal split.

**Detailed answer:** Evidence ghi correlation +0.5909 với target; Spotify popularity ưu ái dữ liệu mới có thể làm model học thời kỳ thay vì chất lượng audio. Đây là generalization risk.

**Project evidence:** `data_leakage_risks.md`; `popularity_limitations.md`.

**Common trap:** Gọi mọi tương quan thời gian là leakage hoặc bỏ qua hoàn toàn time bias.

**Safe wording:** “Available-at-release metadata, but a strong temporal confounder.”

**Follow-up questions:** Có thử model không có year không?

### Q D14 [TRAP] [MUST_KNOW]: Dataset đại diện được gì và không đại diện được gì?

**Short answer:** Nó đại diện cho các record trong historical Spotify-derived snapshot của project. Nó không đại diện đầy đủ mọi quốc gia, nền tảng, genre, thời kỳ mới hay toàn bộ ngành âm nhạc.

**Detailed answer:** Popularity phụ thuộc streams gần đây, playlist, marketing và artist fame; baseline 18 input chủ yếu là audio/release metadata nên bỏ thiếu nhiều driver ngoài model.

**Project evidence:** `popularity_limitations.md`; frontend `6_Limitations.py`.

**Common trap:** “Kết quả áp dụng cho mọi bài hát.”

**Safe wording:** “Descriptive of the available historical platform dataset, not global music.”

**Follow-up questions:** Geographic bias đo chưa? Genre coverage ra sao?

### Q D15 [TRAP] [MUST_KNOW]: Model có dùng dữ liệu năm mới không?

**Short answer:** Locked training period kết thúc năm 2004; validation là 2005–2013 và test là 2014–2021. Vì vậy model không được train trên releases sau 2004 trong split này và không có evidence về dữ liệu sau 2021.

**Detailed answer:** Đây là chủ ý để đánh giá thời gian, nhưng cũng làm performance trên giai đoạn mới khó hơn. Test RMSE cao hơn validation 37,77%.

**Project evidence:** `split_manifest.json`; `validation_test_comparison.json`.

**Common trap:** Nói model “đã cập nhật đến hiện tại.”

**Safe wording:** “Training uses data through 2004; later periods are evaluation, not training.”

**Follow-up questions:** Vì sao không retrain train+validation? Khi nào cần version mới?

### Q D16 [DEEP] [BACKUP]: Nếu hỏi một fact dataset mà project chưa đo thì trả lời sao?

**Short answer:** “Trong phạm vi dự án, nhóm chưa đánh giá riêng yếu tố đó nên em không muốn khẳng định quá mức. Evidence hiện tại cho thấy …”. Sau đó em chỉ nêu fact có source và đề xuất cách kiểm tra.

**Detailed answer:** Ví dụ exact country distribution, license URL, audio fingerprint duplicates và reason chọn dataset chưa có conclusive artifact. Câu trả lời đúng là giới hạn evidence, không đoán.

**Project evidence:** `feature_3_8_qa_source_registry.json` source policy.

**Common trap:** Điền khoảng trống bằng kiến thức chung như thể đó là project fact.

**Safe wording:** “Project evidence does not establish this conclusively.”

**Follow-up questions:** Nếu có thêm thời gian sẽ audit bằng cách nào?
