# Defense Demo Script — HitRadar Pro

**Feature:** 3.8 · **Phase:** 2/5 · **Task:** 3.8.2  
**Người thực hiện:** Minh · **PRIMARY_OPERATOR:** `UNASSIGNED`  
**Primary mode:** `LIVE` · **Fallback:** `OFFLINE_PRECOMPUTED`  
**Thời lượng:** ước lượng lập kế hoạch 5 phút 50 giây cho phần trình bày, cộng 1 phút 30 giây precheck. Chưa có thời lượng chính thức để đối chiếu.

## A. Pre-Demo Check

Thực hiện trước khi hội đồng bắt đầu tính giờ:

```powershell
python scripts/run_all.py
```

Nếu chạy hai terminal riêng:

```powershell
python scripts/run_backend.py
python scripts/run_frontend.py
```

Kiểm tra:

- `GET http://127.0.0.1:8000/health` trả HTTP 200, `status=healthy`, `model_loaded=true`.
- `http://127.0.0.1:8501/_stcore/health` trả HTTP 200.
- UI mở tại `http://localhost:8501`; API URL là `http://localhost:8000`.
- File canonical input có sẵn tại `7.ML/7.10.model_packaging/package/examples/example_input.json` và SHA-256 là `19847ab49e692374203e0fadbdca17e7ca9ae680c1016d2a26dfde6730d33bc0`.
- Mở sẵn Home; không thay đổi input ngẫu nhiên.

Nếu health chưa sẵn sàng, kiểm tra đúng một lần và retry nhanh đúng một lần. Nếu vẫn lỗi, đi thẳng tới mục J.

## B. Opening

**Operator:** mở Home, chỉ vào trạng thái backend và tên ứng dụng.

**Presenter nói:**

> “Tiếp theo phần trình bày, nhóm sẽ demo ba khả năng chính của HitRadar Pro: dự đoán, giải thích và What-if; sau đó xem nhanh dashboard và giới hạn sử dụng. Đây là đầu ra ước lượng của mô hình nghiên cứu, không phải cam kết về thành công thực tế.”

**Kỳ vọng:** Home hiển thị HitRadar Pro, mô tả prototype và cảnh báo limitations.  
**Thời gian mục tiêu:** 30 giây.

## C. Predict

**Action:** vào `🎯 Predict`; dùng đúng 18 giá trị trong canonical input đã chuẩn bị, rồi bấm **Predict Popularity**.

**Presenter nói trước khi bấm:**

> “Input là 18 trường audio và metadata đã được kiểm chứng từ fixture của dự án. Model trả một điểm popularity ước lượng trên thang 0–100; đây không phải xác suất và không phải bảo đảm bài hát sẽ thành hit.”

**Expected live:** UI hiển thị `status=SUCCESS`, model `EXP24-XGB-FINAL-001` phiên bản `1.0.0`, điểm đọc gọn là khoảng **46**. Canonical raw value là `46.421062` với tolerance `±0.001`; không cần đọc sáu chữ số thập phân trước hội đồng.

**Presenter nói sau kết quả:**

> “Với input này, model ước lượng khoảng 46 điểm. Kết quả đang hiển thị là model output cho đúng input vừa nhập.”

**Thời gian mục tiêu:** 75 giây.  
**Fallback:** nếu validation lỗi, sửa input đúng một lần. Nếu API lỗi sau một health check và một retry nhanh, chuyển sang mục J. Predict là bước neo, không bỏ qua; offline chỉ được hiển thị kết quả precomputed đã công bố rõ.

## D. Explain

**Action:** chỉ tiếp tục khi Predict live đã thành công; vào `🔍 Explain` để gọi `POST /explain` với cùng baseline.

**Presenter nói:**

> “Đây là các đóng góp của feature vào dự đoán của model. Nhóm chỉ chọn hai hoặc ba feature có độ lớn đóng góp cao nhất đang hiển thị. Dấu dương hoặc âm mô tả cách model đẩy dự đoán lên hoặc xuống cho input này; SHAP mô tả hành vi của model, không chứng minh quan hệ nhân quả ngoài thực tế.”

**Expected live:** prediction trong Explain khớp Predict; chart/contribution list và cảnh báo noncausal xuất hiện. Không dự đoán trước tên, dấu hoặc giá trị SHAP trong lời thoại.

**Thời gian mục tiêu:** 60 giây.  
**Failure/skip:** technical dry-run ngày 2026-08-11 từng timeout sau 300 giây; final smoke ngày 2026-08-12 đã PASS khoảng 400 ms. Khi bảo vệ vẫn không chờ dài: nếu trang không trả nhanh, nói “Explain live hiện không phản hồi kịp; nhóm bỏ qua bước này theo recovery plan” rồi sang What-if. Offline không có Explain và không được dựng số SHAP thay thế.

## E. What-If

**Action:** giữ đúng baseline của Predict; vào `🔄 What-If`, chọn `energy`, đổi `0.793` thành `0.95`, bấm **Compare Predictions**.

**Presenter nói:**

> “Ta thay đổi một input và xem prediction của model thay đổi ra sao. Hai con số before và after cùng delta trên màn hình là so sánh hai đầu ra của model; chúng không cho biết popularity thực tế sẽ thay đổi như thế nào.”

**Expected live:** `status=SUCCESS`; baseline phải bằng Predict; UI hiển thị before, after và delta. Không nói trước delta dương hay âm. Dry-run hiện tại quan sát delta âm, nhưng kịch bản chỉ đọc kết quả live đang hiển thị và không biến một lần chạy thành quy luật.

**Thời gian mục tiêu:** 60 giây.  
**Failure/skip:** retry tối đa một lần nếu nhanh; nếu không, bỏ qua. Offline không có What-if.

## F. Music Trends

**Action:** vào `📊 Music Trends`; chỉ xem hai phần: caption **Dataset coverage** và chart **Songs per Year**. Không đổi nhiều filter.

**Presenter nói:**

> “Trang này đọc dữ liệu cục bộ và hiển thị thống kê mô tả của đúng file hiện có. Nhóm đọc phạm vi năm và số dòng ngay trên caption, rồi chỉ ra phân bố số bài theo năm. Các chart mô tả dataset đang dùng, không đại diện cho toàn bộ âm nhạc và không hàm ý nhân quả.”

**Expected:** trang tải được dữ liệu và hai visual trên. Dry-run trên file hiện tại ghi nhận 586.672 dòng hợp lệ, phạm vi 1900–2021; nếu caption thay đổi, đọc giá trị trên UI và không dùng số liệu legacy 169.681/1922–2019 để mô tả trang này.

**Thời gian mục tiêu:** 60 giây.  
**Skip rule:** nếu thiếu thời gian, chỉ đọc caption rồi chuyển bước; nếu file lỗi, bỏ qua dashboard và nói rõ dữ liệu cục bộ chưa tải được.

## G. Model Info / Limitations

**Action:** vào `ℹ️ Model Info`, chỉ chỉ ra Model ID/Family/Version; sau đó mở `⚠️ Limitations`.

**Presenter nói:**

> “Ứng dụng đang dùng XGBoost `EXP24-XGB-FINAL-001`, phiên bản `1.0.0`. Đây là student research prototype. Prediction là estimate; SHAP và What-if chỉ mô tả model behavior; kết quả không dùng cho quyết định thương mại hay diễn giải nhân quả.”

Không đọc metric nếu UI không trả metric. Technical dry-run hiện tại của `/model-info` trả `metrics=null`, vì vậy script không gắn số metric vào bước này.

**Thời gian mục tiêu:** 45 giây.  
**Fallback:** Model Info offline chỉ là static validated snapshot và phải được gọi đúng tên; Limitations là trang local.

## H. Demo Closing Line

> “Tóm lại, demo đã nối một input đã kiểm chứng với prediction, công cụ quan sát model và phần giới hạn sử dụng. Nhóm chỉ khẳng định những gì đang hiển thị và luôn tách model behavior khỏi tác động thực tế. Cảm ơn hội đồng.”

**Thời gian mục tiêu:** 20 giây.

## I. Failure Recovery

Áp dụng cây quyết định trong `feature_3_8_demo_failure_tree.md`. Quy tắc chung:

1. Không retry vô hạn: tối đa một lần sửa input hoặc một lần retry nhanh.
2. Predict thất bại kéo Explain/What-if sang trạng thái skip; không dùng baseline khác.
3. Explain timeout thì bỏ qua, không chờ và không dựng SHAP.
4. UI fatal thì dùng đúng asset có thật. Hiện screenshot chưa được chụp và video vẫn `MANUAL_RECORDING_REQUIRED`, nên không tuyên bố chúng sẵn sàng.

## J. Offline Fallback

**Phân biệt mode:** LIVE phải có health 200 + `model_loaded=true` và response mới từ API. `OFFLINE_PRECOMPUTED` chỉ dùng canonical evidence đã tính trước; không có request inference mới. Hợp đồng offline của Feature 3.6 đã được viết nhưng UI implementation chưa được xác nhận, nên operator phải dùng evidence file/slide đã chuẩn bị và không gọi đó là app live.

**Câu bắt buộc, nói nguyên văn:**

> “API live hiện không khả dụng, nên nhóm chuyển sang Offline Demo Mode với kết quả đã được tính và kiểm chứng trước. Phần này không thực hiện live inference.”

**Thứ tự fallback:**

1. Hiển thị canonical input và precomputed output `46.421062` / display `46` từ `demo/offline/evidence/`.
2. Nói rõ Explain và What-if `NOT_AVAILABLE`; không minh họa bằng số tự tạo.
3. Music Trends chỉ tiếp tục nếu local dataset/page vẫn tải được.
4. Model Info dùng validated static snapshot; Limitations dùng trang local hoặc nội dung trong script.
5. Screenshot/video chỉ dùng sau khi Phase 4 thực sự tạo và kiểm tra file; hiện tại cả hai chưa sẵn sàng.

## Flow rút gọn khi thiếu thời gian

Home 15s → Predict 60s → Explain 30s nếu phản hồi ngay → What-if 45s → Trends chỉ đọc caption 20s → Model Info/Limitations 30s → End 15s. Predict không được bỏ; Explain/What-if phải bỏ nếu live không sẵn sàng và không được thay bằng kết quả offline giả.
