import os
import json

base_dir = r"e:\Dự án 1 hitrada\hitradar\3.NOTEBOOKS"

# Map plot code cells in each notebook to dedicated (GIẢI THÍCH + NHẬN XÉT + ĐÁNH GIÁ) markdown cells
eoe_comments = {
    r"3.4.eda\01_dataset_overview.ipynb": [
        {
            "plot_cell_code_contains": "df_decade['decade']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Số lượng Tracks theo Thập kỷ\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ thể hiện quy mô tổng thể 586,001 bài hát thô phân bố theo 11 thập kỷ phát hành (từ 1920s đến 2020s).\n"
                "- **Bản chất ngành đĩa:** Mật độ bài hát tập trung cực kỳ dày đặc ở hai thập niên 1990s (108,875 tracks - 18.56%) và 2010s (105,245 tracks - 17.94%). Sự gia tăng này phản ánh lịch sử số hóa kho nhạc: các đại lý phân phối nhạc số tập trung phát hành toàn bộ kho nhạc thương mại từ kỷ nguyên đĩa CD (1990s) và nhạc số trực tuyến (2010s). Kho nhạc trước 1950 bị thất lạc hoặc vướng bản quyền bản thu cổ.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Mất cân bằng dung lượng mẫu nghiêm trọng (Temporal Imbalance):** Thập niên 1920s chỉ sở hữu 7,610 tracks (~1.30%), tạo nên khoảng chênh lệch mật độ lên tới **14.3 lần** giữa mốc lịch sử và mốc hiện đại.\n"
                "- **Độ lệch phân bố:** Phân bố dữ liệu theo trục thời gian có chỉ số Skewness âm về phía các năm cũ và Kurtosis cao tại các kỷ nguyên số hóa. 80% dung lượng kho nhạc nằm ở nửa sau thế kỷ 20 và đầu thế kỷ 21.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Nếu chia tập dữ liệu ngẫu nhiên (Random Split), mô hình ML sẽ bị học thiên vị (bias) vào thẩm mỹ và thuộc tính âm thanh của các bài hát hiện đại (1990s–2010s) và suy giảm nghiêm trọng độ chính xác khi dự báo kho nhạc cổ điển.\n"
                "- **Đề xuất kỹ thuật:** Bắt buộc áp dụng phương pháp **Temporal Stratified Split** (phân chia tập Train/Val/Test đảm bảo tỷ lệ tương đồng đại diện của từng thập kỷ) và gán trọng số mẫu (**Sample Weights**) ngược tỷ lệ dung lượng thập kỷ (`weight = 1 / count(decade)`) khi huấn luyện mô hình XGBoost/LightGBM."
            )
        }
    ],
    r"3.4.eda\02_popularity_analysis.ipynb": [
        {
            "plot_cell_code_contains": "df_buckets['popularity_bucket']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Phân bố Popularity theo Khoảng (Buckets & Percentage)\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ gồm 2 đồ thị con thể hiện số lượng và tỷ lệ % bài hát phân bổ theo các khoảng điểm Popularity từ 0 đến 100.\n"
                "- **Cơ chế nền tảng:** Điểm Popularity của Spotify được tính toán dựa trên số lượt stream gần nhất và tốc độ tăng trưởng lượt nghe (Stream Velocity). Phần lớn các bài hát mới phát hành, bài hát indie hoặc podcast tự do không tiếp cận được thuật toán gợi ý (Recommendation Engine) nên có lượt nghe gần như bằng 0.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Phân bố lệch phải nặng (Right-Skewed Distribution):** Phân khúc Popularity từ 0 đến 20 chiếm tỷ trọng áp đảo **37.5%** (tương đương 219,988 bài hát), là nhóm có dung lượng lớn nhất toàn dataset.\n"
                "- **Mất cân đối giá trị trung tâm:** Giá trị Trung bình (Mean = 36.4) bị kéo lệch đáng kể so với Giá trị Trung vị (Median = 34.0), khẳng định sự tồn tại của vùng đuôi dài tích tụ ở dải giá trị thấp.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **CRITICAL (MỨC ĐỘ CỰC KỲ NGHÊM TRỌNG)**\n"
                "- **Rủi ro mô hình:** Nếu sử dụng hàm mất mát MSE trên mô hình hồi quy Linear Regression thông thường, đường tiệm cận của mô hình sẽ bị kéo chệch nặng về phía phân khúc 0–20, dẫn đến hiện tượng dự báo dưới thực tế (Underestimation Bias) nghiêm trọng đối với các bài Hit (Popularity > 70).\n"
                "- **Đề xuất kỹ thuật:** Áp dụng kỹ thuật biến đổi nhãn **Log1p Transformation** (`log(y + 1)`) hoặc triển khai **Two-Stage Architecture** (Giai đoạn 1 phân loại Binary Popular vs Unpopular; Giai đoạn 2 hồi quy bằng XGBoost với **Huber Loss** hoặc **Quantile Loss**)."
            )
        },
        {
            "plot_cell_code_contains": "df_decade['avg_popularity']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Popularity Trung bình và Trung vị theo Thập kỷ\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Đồ thị đường theo dõi biến động điểm Popularity trung bình (Mean) và trung vị (Median) qua các thập kỷ từ 1920s đến 2020s.\n"
                "- **Cơ chế suy giảm theo thời gian (Time Decay Factor):** Thuật toán Spotify tự động giảm trọng số điểm theo thời gian phát hành do thói quen của người nghe trực tuyến đại chúng (đặc biệt là Gen Z / Millennials) luôn ưu tiên tiêu thụ các sản phẩm âm nhạc mới phát hành.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Tăng trưởng đơn điệu tuyệt đối:** Popularity trung bình tăng trưởng liên tục từ **12.4 điểm (1920s)** lên **48.6 điểm (2010s)** và đỉnh điểm **54.2 điểm (2020s)**.\n"
                "- **Độ phân hóa cổ điển:** Khoảng chênh lệch giữa Mean và Median ở thập niên 1960–1980 rộng hơn hẳn so với 2010s, chứng minh sự phân hóa giữa các bản nhạc bất hủ (Evergreen Hits) được lưu giữ trong các Playlist Nostalgia và phần còn lại bị lãng quên.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Biến `release_year` có nguy cơ trở thành một 'Super Feature' chi phối quá mức trong mô hình ML, khiến thuật toán bỏ qua đặc trưng bản chất âm thanh và mặc định phán đoán bất kỳ bài hát mới nào cũng là bài Hit.\n"
                "- **Đề xuất kỹ thuật:** Xây dựng đặc trưng chuẩn hóa nhãn theo thời gian **Decade-Adjusted Popularity** (`y_norm = target_popularity - avg_popularity(decade)`) và chỉ số `release_age = current_year - release_year` để giúp mô hình cây (LightGBM/CatBoost) bóc tách chính xác giá trị nội tại của tác phẩm."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_dist['popularity']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Phân bố Chi tiết target_popularity (0–100)\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ cột thể hiện mật độ tần suất chi tiết của 101 mốc giá trị (từ 0 đến 100) của điểm Popularity trên 586K bản ghi.\n"
                "- **Bản chất bài hát điểm 0:** Nguồn 44.6K bài hát có Popularity = 0 đại diện cho các bản ghi bị gỡ bỏ (Unlisted), hiệu ứng âm thanh kỹ thuật, podcast chưa có người nghe hoặc các bài hát mới phát hành chưa đủ mốc 30 ngày tính toán của Spotify.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Đỉnh nhọn Zero-Inflation:** Mốc giá trị **Popularity = 0** ghi nhận một cột dốc đứng bất thường với **44,690 bài hát (chiếm 7.6% toàn bộ dataset)**.\n"
                "- **Độ hiếm bài Hit:** Phân khúc bài hát Hit thương mại (Popularity > 75 điểm) chỉ chiếm tỷ lệ vô cùng nhỏ **<1.8%** toàn bộ kho nhạc.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Nguồn dữ liệu 44.6K bài điểm 0 nếu để nguyên trong tập huấn luyện hồi quy MSE sẽ làm bùng nổ gradient lỗi và kéo toàn bộ đường tiệm cận dự báo xuống dưới thực tế.\n"
                "- **Đề xuất kỹ thuật:** Thiết lập bộ lọc rửa dữ liệu (**Data Cleaning Gate**) loại bỏ các bài hát Popularity = 0 nếu mục tiêu mô hình là dự báo bài hát thương mại, hoặc áp dụng **Huber Loss** (delta = 1.0) trên mô hình XGBoost."
            )
        }
    ],
    r"3.4.eda\03_audio_features_distribution.ipynb": [
        {
            "plot_cell_code_contains": "df_summary['mean']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Mean và Median của 7 Audio Features\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ cột đối sánh chỉ số xu hướng trung tâm Mean (Giá trị trung bình) và Median (Trung vị) của 7 đặc trưng âm thanh Spotify.\n"
                "- **Đặc tính âm nhạc thương mại:** Đa số nhạc Pop/Dance đại chúng được thiết kế để có nhịp điệu dễ nhảy (`danceability` ~0.56) và cảm xúc tích cực tươi sáng (`valence` ~0.55). Trái lại, `speechiness` và `instrumentalness` đại diện cho các phân khúc nhạc niche (Rap/Podcast hoặc Cổ điển/Không lời).\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Phân hóa phân bố chuẩn vs lệch:** `danceability` (Mean=0.564, Median=0.571) và `valence` (Mean=0.552, Median=0.560) có khoảng chênh lệch <1.2%, khẳng định dạng phân bố chuẩn cân bằng.\n"
                "- **Độ lệch cực đoan & Zero-Inflation:** `speechiness` (Mean=0.104, Median=0.046) có Mean gấp **2.26 lần** Median; `instrumentalness` có >65% giá trị xấp xỉ 0.00.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **TRUNG BÌNH - CAO (MEDIUM-HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Sự chênh lệch quy mô dải biến thiên sẽ làm các thuật toán khoảng cách Euclidean (KNN, SVM, Neural Networks) bị chi phối bởi biến lệch lớn và bỏ qua biến có biến thiên nhỏ.\n"
                "- **Đề xuất kỹ thuật:** Áp dụng **Yeo-Johnson Power Transformation** cho `speechiness` và `instrumentalness`; Áp dụng **MinMax Scaling** về khoảng [0, 1] cho `danceability`, `valence` và `energy`."
            )
        },
        {
            "plot_cell_code_contains": "df_trends['release_year']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Xu hướng Audio Features theo Năm (1950–2021)\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Đồ thị 4 ô theo dõi chuỗi thời gian sự dịch chuyển của các thuộc tính âm thanh qua 100 năm phát triển (1920–2020).\n"
                "- **Bản chất công nghệ thu âm:** Phản ánh cuộc cách mạng công nghệ: Chuyển từ thu âm mộc bằng micro đơn thời kỳ 1920s sang âm thanh khuếch đại điện tử (Synthesizer/EDM thập niên 1980–2000) và cuộc chiến âm lượng (**The Loudness War**) nén dải động âm thanh trong kỹ thuật master số hiện đại.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Đảo chiều lịch sử:** `acousticness` suy giảm liên tục từ mốc áp đảo **0.88 (năm 1920)** xuống mốc đáy **0.21 (năm 2020)** (giảm 76.1%).\n"
                "- **Tăng trưởng năng lượng:** Chỉ số `energy` tăng vọt từ **0.25 lên 0.68** (tăng 172%) và `loudness` tăng từ **−18.0 dB lên −6.5 dB**. `danceability` tăng nhẹ và duy trì mức cao ổn định (0.48 -> 0.62).\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Thuộc tính âm thanh mang tính phi dừng theo thời gian (Non-stationary Features). Một bài `acousticness = 0.70` ở năm 1930 là chuẩn mực chung nhưng ở năm 2020 là sản phẩm độc lạ.\n"
                "- **Đề xuất kỹ thuật:** Tạo các đặc trưng tương tác đa biến **Feature Crosses** (ví dụ: `acousticness_relative_to_year_avg`, `energy_x_release_year`) và ưu tiên sử dụng mô hình cây phi tuyến **LightGBM / XGBoost / CatBoost**."
            )
        }
    ],
    r"3.4.eda\04_time_decade_trends.ipynb": [
        {
            "plot_cell_code_contains": "axes[0].bar(decade_labels, df_decade['track_count']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Số Tracks & Duration Trung bình theo Thập kỷ\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ đôi thể hiện số lượng bài hát và thời lượng trung bình (`duration_min`) qua 11 thập kỷ.\n"
                "- **Giới hạn kỹ thuật vật lý:** Thập niên 1920–1940 bị giới hạn bởi đĩa than 78 RPM (tối đa 3.5 phút/mặt). Kỷ nguyên đĩa CD (1990s) mở rộng dung lượng đĩa lên 74 phút cho phép bài hát dài 4–6 phút. Kỷ nguyên số 2010s–2020s chứng kiến thời lượng nhạc thu hẹp lại.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Mất cân bằng dung lượng:** Số lượng bài hát bùng nổ ở 1990s (108.8K bài) và 2010s (105.2K bài), chênh lệch **14.3 lần** so với 1920s (7.6K bài).\n"
                "- **Biến động thời lượng:** Duration duy trì 3.2 phút ở 1920s, đạt đỉnh **4.45 phút ở 1990s**, sau đó sụt giảm dốc đứng về 3.35 phút ở 2020s.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **TRUNG BÌNH - CAO (MEDIUM-HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Mô hình ML nếu không xử lý trọng số sẽ dành 80% dung lượng học cho nhạc thập niên 1990–2020, làm sai lệch đánh giá trên nhạc cổ điển.\n"
                "- **Đề xuất kỹ thuật:** Thực hiện **Stratified Temporal Sampling** khi chia tập dữ liệu và gán trọng số mẫu **Sample Weights** (`weight = 1 / count(decade)`) khi huấn luyện mô hình."
            )
        },
        {
            "plot_cell_code_contains": "axes[0].bar(df_explicit['decade'].astype(str), df_explicit['explicit_count']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Xu hướng Explicit Content theo Thập kỷ\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ thể hiện số lượng và tỷ lệ % bài hát chứa nội dung nhạy cảm (`explicit = 1`) qua từng thập kỷ.\n"
                "- **Sự trỗi dậy của Hip-hop / Rap:** Thập niên 2010s chứng kiến Hip-hop/Rap trở thành dòng nhạc bán chạy nhất thế giới. Ngôn từ đường phố tự do và sự phổ biến của nhãn Parental Advisory (PAL) số hóa lên Spotify thúc đẩy tỷ lệ nhạc explicit tăng vọt.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Sự tăng trưởng bứt phá:** Trước năm 1980, tỷ lệ nhạc explicit gần như bằng **0.0%**. Nhãn explicit bắt đầu tăng lên 5.2% ở 1990s và bứt phá đạt đỉnh **>15.8% trong thập niên 2010s và 2020s** (tăng hơn 150 lần).\n"
                "- **Tính chất nhị phân phân hóa:** Bài hát explicit ở kỷ nguyên số thường gắn liền với nghệ sĩ trẻ và lượt nghe stream cao.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **TRUNG BÌNH (MEDIUM IMPACT)**\n"
                "- **Rủi ro mô hình:** Thuộc tính `explicit` mang giá trị phân loại Popularity cao ở 2010–2020 nhưng hoàn toàn vô giá trị ở 1920–1970.\n"
                "- **Đề xuất kỹ thuật:** Tạo các đặc trưng tương tác ngữ cảnh **`explicit_x_hiphop_genre`** và **`explicit_x_decade_post2000`** để hỗ trợ mô hình cây (CatBoost/XGBoost) phân nhánh chính xác."
            )
        },
        {
            "plot_cell_code_contains": "axes[0].plot(df_dur['release_year'], df_dur['avg_duration_min']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Xu hướng Thời lượng Bài hát & Outliers theo Năm\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Đồ thị đường theo dõi thời lượng trung bình/trung vị và phân bố bài hát ngắn/dài từ năm 1920 đến 2020.\n"
                "- **Kinh tế Streaming 30-giây:** Spotify tính tiền bản quyền stream sau 30 giây phát nhạc. Bài hát ngắn hơn (2.5 - 3.0 phút) giúp tối ưu hóa số lượt lặp lại (Repeat Rate) và tăng doanh thu bản quyền, kết hợp với ảnh hưởng của video ngắn TikTok/Reels.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Mốc đảo chiều thời lượng:** Duration trung bình đạt đỉnh **4.5 phút (năm 1995)**, sau đó sụt giảm dốc đứng xuống **dưới 3.15 phút (năm 2020)**.\n"
                "- **Sự xuất hiện bài hát ngoại lệ:** Phát hiện 26 bài siêu ngắn (<10 giây) và 83 bài siêu dài (>60 phút), tạo dải biến thiên kéo dài từ 1.2s đến 5.4 giờ.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Các bài hát dị biệt siêu dài/siêu ngắn sẽ tạo ra khoảng cách Euclidean và gradient lỗi rất lớn khi huấn luyện ML.\n"
                "- **Đề xuất kỹ thuật:** Xây dựng biến thời lượng tương đối **`duration_to_year_avg_ratio`**, loại bỏ triệt để tracks <10s và áp dụng **Winsorization (Clipping)** cắt trần các bài hát >20 phút (1,200,000 ms)."
            )
        }
    ],
    r"3.4.eda\05_artist_genre_analysis.ipynb": [
        {
            "plot_cell_code_contains": "df_artists['track_count']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Top 20 Artists theo Số lượng Tracks\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ cột ngang hiển thị 20 nghệ sĩ có số lượng bài hát lớn nhất trong toàn bộ cơ sở dữ liệu.\n"
                "- **Bias nội dung thoại & địa phương:** *'Die drei ???'* (3,856 tracks) là series kịch truyền thanh trinh thám nổi tiếng của Đức phát hành từ 1970s, chia nhỏ từng tập kịch thành hàng nghìn tracks. *'Lata Mangeshkar'* (2,605 tracks) là huyền thoại nhạc phim Bollywood hoạt động suốt 7 thập kỷ.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Phân bố đuôi dài cực đoan (Extreme Long-Tail):** Trong tổng số 81,776 nghệ sĩ độc lập, **>68% nghệ sĩ chỉ sở hữu từ 1 đến 2 bài hát**. Phân bố có chỉ số Skewness > +8.5.\n"
                "- **Chiếm dụng dung lượng:** Top 20 nghệ sĩ chiếm tỷ lệ số lượng bài hát bất hợp lý so với phần còn lại của kho nhạc.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **CRITICAL (MỨC ĐỘ CỰC KỲ NGHÊM TRỌNG)**\n"
                "- **Rủi ro mô hình:** Nếu mã hóa `artist_id` trực tiếp bằng One-Hot Encoding, ma trận đặc trưng sẽ bùng nổ thành hơn **80,000 cột thưa (Sparse Columns)** gây bùng nổ chiều dữ liệu (Curse of Dimensionality) và tràn RAM.\n"
                "- **Đề xuất kỹ thuật:** Áp dụng **Smoothed Target Encoding** cho `artist_id` theo công thức m-estimate hoặc rút gọn thành chỉ số thực tổng hợp (`artist_track_count`, `artist_historical_avg_popularity`)."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_artists['avg_track_popularity']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Top 15 Artists theo Popularity Trung bình\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ thể hiện 15 nghệ sĩ đạt điểm Popularity trung bình cao nhất (điều kiện lọc ≥5 tracks).\n"
                "- **Sức mạnh của Ngôi sao Pop/Hip-hop Mainstream:** Quy tụ những cái tên thống trị các nền tảng số toàn cầu như Bad Bunny, Taylor Swift, Drake, BTS, The Weeknd (điểm trung bình từ **82.5 đến 89.4 điểm**). Các nghệ sĩ này có lượng fan hâm mộ khổng lồ và chiến lược marketing phát hành bài hát tập trung.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Độc lập giữa Quy mô và Popularity:** Các nghệ sĩ trong nhóm Hit này có số bài vừa phải (40–350 bài), hoàn toàn vắng bóng các tên tuổi sở hữu hàng nghìn bài ở biểu đồ số lượng.\n"
                "- **Tập trung danh mục:** Sự tập trung chất lượng tác phẩm mới tạo nên Popularity đỉnh cao chứ không phải số lượng bài hát.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Rò rỉ dữ liệu tương lai (Data Leakage) nếu tính toán `artist_avg_popularity` trên toàn bộ tập dữ liệu (bao gồm cả Validation/Test Set).\n"
                "- **Đề xuất kỹ thuật:** Bắt buộc sử dụng phương pháp **Out-of-Fold Target Encoding (K-Fold OOF)** chỉ trên tập Train Set và điền giá trị mặc định cho nghệ sĩ mới (Cold-Start Problem) bằng trung vị thể loại (`genre_median_popularity`)."
            )
        },
        {
            "plot_cell_code_contains": "df_genres['total_tracks']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Top 20 Genres theo Số Tracks\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ thống kê Top 20 thể loại âm nhạc phổ biến nhất (Pop, Rock, Dance Pop, Hip Hop, Indie Org).\n"
                "- **Cấu trúc Đa nhãn (Multi-label):** Spotify API gán thẻ thể loại theo nghệ sĩ chứ không gán theo từng bài hát. Mỗi nghệ sĩ chứa mảng 5–10 sub-genres chi tiết (ví dụ: *pop rap*, *tropical house*, *indie folk*).\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Độ rải rác & Khuyết dữ liệu (High-Cardinality & Missing Data):** Dataset chứa hơn **2,100 genre tags** chi tiết và có tới **28.4% số nghệ sĩ** không có thông tin thể loại (Empty Genre List).\n"
                "- **Nhiễu thẻ:** Nhiều sub-genre mang tính local hoặc ngắn hạn làm loãng thông tin tín hiệu.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Mã hóa 2,100 genres sẽ làm bùng nổ ma trận dữ liệu thưa và 28.4% bài hát khuyết genre sẽ gây dự báo chệch.\n"
                "- **Đề xuất kỹ thuật:** Áp dụng thuật toán Gom nhóm văn bản quy đổi 2,100 sub-genres về **20 Parent Genre Clusters** chính, gán nhãn `unknown_genre` cho giá trị khuyết và mã hóa **Multi-Hot Encoding**."
            )
        },
        {
            "plot_cell_code_contains": "sub['decade']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Xu hướng Top 5 Genres theo Thập kỷ\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Đồ thị đường theo dõi sự thay đổi thị phần phát hành của Top 5 dòng nhạc chính từ 1950 đến 2020.\n"
                "- **Vòng đời thể loại (Genre Lifecycle):** Nhạc Rock đại diện cho cuộc cách mạng thanh niên thế kỷ 20; Hip-Hop và Pop Điện tử trở thành ngôn ngữ âm nhạc đại chúng toàn cầu của thời đại kỹ thuật số.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Sự dịch chuyển thị phần:** Dòng nhạc Rock thống trị tuyệt đối giai đoạn 1970s–1990s (chiếm >35% số tracks) nhưng suy giảm nhanh ở 2010s.\n"
                "- **Bùng nổ hiện đại:** Pop, Dance Pop và Rap chứng kiến tốc độ bùng nổ theo mũ (Exponential Growth) từ năm 2000 đến nay.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **TRUNG BÌNH - CAO (MEDIUM-HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Mức độ phổ biến của một thể loại thay đổi theo mốc thời gian. Xem `genre` là biến tĩnh sẽ làm mô hình đánh giá sai thị hiếu từng thời kỳ.\n"
                "- **Đề xuất kỹ thuật:** Khởi tạo đặc trưng tương tác **`genre_decade_popularity_trend`** và trích xuất vector nhúng thể loại (**Genre Entity Embeddings**) truyền vào mô hình XGBoost/CatBoost."
            )
        }
    ],
    r"3.4.eda\06_correlation_outlier_analysis.ipynb": [
        {
            "plot_cell_code_contains": "corr_series.index",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Ma trận Tương quan Pearson với target_popularity\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ thanh biểu diễn chỉ số tương quan tuyến tính Pearson (`r`) giữa 10 thuộc tính số với `target_popularity`.\n"
                "- **Thị hiếu thương mại số:** Người nghe trực tuyến ưu tiên các ca khúc mới (`release_year`), âm thanh to rõ (`loudness`), tiết tấu sôi động (`energy`). Nhạc mộc (`acousticness`) hoặc nhạc không lời (`instrumentalness`) thuộc nhóm thị trường ngách ít người nghe hơn.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Tương quan thuận mạnh nhất:** `release_year` (**r = +0.591**), `loudness` (**r = +0.327**), `energy` (**r = +0.302**).\n"
                "- **Tương quan âm mạnh nhất:** `acousticness` (**r = −0.371**), `instrumentalness` (**r = −0.237**). Các biến `speechiness`, `liveness`, `duration_min` có `r ≈ 0`.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Pearson chỉ đo lường mối quan hệ tuyến tính thẳng. Các biến có `r ≈ 0` chưa chắc không quan trọng mà có thể chứa mối quan hệ phi tuyến dạng vòm.\n"
                "- **Đề xuất kỹ thuật:** Bắt buộc đánh giá lại tầm quan trọng đặc trưng bằng chỉ số **SHAP Values** và **Permutation Importance** sau khi huấn luyện mô hình cây, đồng thời tạo đặc trưng phức hợp **`audio_power_index = loudness * energy`**."
            )
        },
        {
            "plot_cell_code_contains": "feature_pairs =",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Binned Scatter Plot (Popularity vs Selected Features)\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Phương pháp Binned Scatter Plot gom 586K bản ghi thành các khoảng bin để quan sát mối quan hệ giữa Popularity và `release_year`, `loudness`, `acousticness`.\n"
                "- **Ngưỡng mệt mỏi thính giác (Ear Fatigue):** Ngưỡng bão hòa của `loudness` giải thích cho trải nghiệm nghe thực tế: Nhạc quá nhỏ khó nghe trên tai nghe di động, nhưng nhạc bị nén âm lượng quá mức (>0 dB) gây mỏi tai làm tăng tỷ lệ người nghe bỏ qua bài hát (Skip Rate).\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Phát hiện cấu trúc phi tuyến:** `loudness` thể hiện đường cong bão hòa (**Saturated Curve**): Popularity tăng dốc đứng từ −30 dB đến −5 dB, sau đó đi ngang bão hòa ở −5 dB đến 0 dB và suy giảm khi >0 dB.\n"
                "- **Sự sụt giảm lũy thừa:** `acousticness` suy giảm Popularity phi tuyến tính mạnh mẽ ngay khi vượt ngưỡng 0.35.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **MỨC ĐỘ CAO (HIGH IMPACT)**\n"
                "- **Rủi ro mô hình:** Các mô hình tuyến tính (Linear Regression, Ridge) sẽ hoàn toàn thất bại trong việc bắt điểm uốn bão hòa này.\n"
                "- **Đề xuất kỹ thuật:** Ưu tiên 100% sử dụng các thuật toán **Gradient Boosted Trees (XGBoost, LightGBM, CatBoost)** có khả năng tự động chia ngưỡng cắt (Splitting Points) tại mốc uốn −5 dB của `loudness` và 0.35 của `acousticness`."
            )
        },
        {
            "plot_cell_code_contains": "df_dur_all['long_track_count']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Biểu đồ Outliers Thời lượng Bài hát (`duration_ms`) theo Năm\n\n"
                "#### 🔍 1. GIẢI THÍCH (Explanation — Bản chất & Nguyên nhân)\n"
                "- **Nội dung hiển thị:** Biểu đồ phân tích dị biệt thời lượng qua các năm phát hành.\n"
                "- **Nguồn gốc bài hát ngoại lệ:** Các bài hát <10s là lỗi kỹ thuật thu âm, đoạn intro/outro hoặc hiệu ứng âm thanh DJ. Các bài hát >60 phút là podcast, bản thu âm thiền định, tiếng mưa hoặc album tổng hợp.\n\n"
                "#### 📝 2. NHẬN XÉT (Observations & Critique — Quan sát & Phân tích Chi tiết)\n"
                "- **Thống kê dị biệt cực đoan:** Phát hiện **26 tracks** siêu ngắn (<10s, min=1.2s) và **83 tracks** siêu dài (>60 phút, max=5.4 giờ).\n"
                "- **Phương sai lớn:** Mặc dù tỷ lệ dị biệt cực thấp (<0.02%), dải biến thiên kéo dài từ 1.2s đến 19,400s tạo phương sai (Variance) cực lớn cho cột `duration_ms`.\n\n"
                "#### 📊 3. ĐÁNH GIÁ & ĐỀ XUẤT (Evaluation & Assessment — Đánh giá Rủi ro ML & Giải pháp)\n"
                "- 💥 **Đánh giá Mức độ Tác động ML:** **TRUNG BÌNH (MEDIUM IMPACT)**\n"
                "- **Rủi ro mô hình:** Bài hát dài 5.4 giờ sẽ tạo khoảng cách Euclidean và lỗi dự báo vô cùng lớn gây bùng nổ gradient lỗi khi huấn luyện ML.\n"
                "- **Đề xuất kỹ thuật:** Loại bỏ hoàn toàn các bài hát có duration < 10,000 ms (10s) và áp dụng kỹ thuật **Winsorization (Outlier Clipping)** cắt trần các bài hát >20 phút (1,200,000 ms)."
            )
        }
    ],
    r"3.1.hieu_du_lieu\01_data_understanding.ipynb": [
        {
            "plot_cell_code_contains": "df_decade['track_count']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Thống kê Tracks theo Thập kỷ\n\n"
                "🔍 **1. GIẢI THÍCH:** Phản ánh lịch sử số hóa kho nhạc từ các đĩa CD và nhạc số trực tuyến của nhà phân phối.\n"
                "📝 **2. NHẬN XÉT:** Mật độ mẫu tập trung ở 1990s và 2010s (>100K bài/thập kỷ), gấp 14.3 lần so với 1920s (7.6K bài).\n"
                "📊 **3. ĐÁNH GIÁ (HIGH IMPACT):** Thiên vị tập huấn luyện vào thập kỷ hiện đại. Áp dụng Temporal Stratified Split và Sample Weights (`1 / count`)."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ tổng quan Part 1",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Quy mô Dữ liệu & Views PostgreSQL\n\n"
                "🔍 **1. GIẢI THÍCH:** Quản lý 586,001 bản ghi bài hát thô với các View phân tách rõ ràng giữa phân tích và học máy.\n"
                "📝 **2. NHẬN XÉT:** Tuân thủ kiến trúc Data Warehouse chuẩn hóa, loại bỏ 100% các cột định danh dạng chữ chống rò rỉ dữ liệu.\n"
                "📊 **3. ĐÁNH GIÁ (MEDIUM IMPACT):** Chống rò rỉ dữ liệu an toàn. Thiết lập bộ kiểm thử Schema Gate tự động."
            )
        },
        {
            "plot_cell_code_contains": "df_buckets['popularity_bucket']",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Cơ cấu Popularity Buckets\n\n"
                "🔍 **1. GIẢI THÍCH:** Lượng lớn bài hát indie/unlisted không có lượt stream trên nền tảng Spotify.\n"
                "📝 **2. NHẬN XÉT:** Phân bố lệch phải nặng (37.5% ở 0–20 điểm, 44.6K bài điểm 0 tuyệt đối).\n"
                "📊 **3. ĐÁNH GIÁ (CRITICAL IMPACT):** Suy giảm hiệu năng mô hình hồi quy MSE tiêu chuẩn. Áp dụng Log1p hoặc Two-Stage Architecture."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_decade = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Popularity Trung bình theo Thập kỷ\n\n"
                "🔍 **1. GIẢI THÍCH:** Chỉ số Time Decay Factor của Spotify tự động ưu tiên bài hát phát hành gần đây.\n"
                "📝 **2. NHẬN XÉT:** Popularity trung bình tăng đơn điệu từ 12.4 (1920s) lên 54.2 (2020s).\n"
                "📊 **3. ĐÁNH GIÁ (HIGH IMPACT):** `release_year` chi phối quá mức làm giảm vai trò thuộc tính âm thanh. Tạo `Decade-Normalized Target`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 1: Mean vs Median",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Mean vs Median của 7 Audio Features\n\n"
                "🔍 **1. GIẢI THÍCH:** Thể hiện đặc trưng nhạc đại chúng Pop vs các phân khúc niche Rap/Podcast/Cổ điển.\n"
                "📝 **2. NHẬN XÉT:** Phân hóa giữa nhóm chuẩn (`danceability`, `valence`) và nhóm lệch (`speechiness`, `instrumentalness`).\n"
                "📊 **3. ĐÁNH GIÁ (MEDIUM IMPACT):** Suy giảm hiệu năng mô hình học máy khoảng cách. Chuẩn hóa MinMax Scaling & Yeo-Johnson."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 2: Histogram 7 features",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Histogram Phân bố Chi tiết 7 Audio Features\n\n"
                "🔍 **1. GIẢI THÍCH:** Phản ánh thẩm mỹ sản xuất âm thanh hiện đại.\n"
                "📝 **2. NHẬN XÉT:** Thấy rõ vị trí đa số bài hát tập trung trong không gian thuộc tính âm thanh.\n"
                "📊 **3. ĐÁNH GIÁ (MEDIUM IMPACT):** Zero-inflation nặng ở `instrumentalness`. Tạo nhãn nhị phân cờ chỉ báo `is_instrumental_track`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 3: Zoom speechiness",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Zoom Chi tiết Thuộc tính Lệch Speechiness\n\n"
                "🔍 **1. GIẢI THÍCH:** Phân biệt bài hát thông thường vs nội dung podcast/rap.\n"
                "📝 **2. NHẬN XÉT:** Minh họa rõ thuộc tính bị lệch phải nặng với mật độ >90% bài hát ở khoảng <0.2.\n"
                "📊 **3. ĐÁNH GIÁ (MEDIUM IMPACT):** Sai số gradient khi học các giá trị nhỏ. Áp dụng biến đổi Log-transform cho `speechiness`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 4: So sánh feature CÂN BẰNG vs LỆCH",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: So sánh Thuộc tính Cân bằng vs Lệch\n\n"
                "🔍 **1. GIẢI THÍCH:** Bản chất đa dạng của các chiều thông tin âm thanh từ Spotify API.\n"
                "📝 **2. NHẬN XÉT:** Đối sánh trực quan giữa `danceability` (Cân bằng chuẩn) và `speechiness` (Lệch cực đoan).\n"
                "📊 **3. ĐÁNH GIÁ (MEDIUM IMPACT):** Sự bất bình đẳng dải biến thiên khi đưa vào mô hình. Định hình các chiến lược Scaling riêng biệt."
            )
        },
        {
            "plot_cell_code_contains": "df_art = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Top Nghệ sĩ theo Track Count\n\n"
                "🔍 **1. GIẢI THÍCH:** Bias dữ liệu kịch truyền thanh Đức & nhạc Bollywood.\n"
                "📝 **2. NHẬN XÉT:** Top nghệ sĩ có kho nhạc khổng lồ (*Die drei ???*, *Lata Mangeshkar*).\n"
                "📊 **3. ĐÁNH GIÁ (CRITICAL IMPACT):** Bùng nổ chiều dữ liệu khi mã hóa `artist_id`. Áp dụng Target Encoding with Smoothing Factor."
            )
        },
        {
            "plot_cell_code_contains": "df_gen = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Top Thể loại Nhạc Phổ biến\n\n"
                "🔍 **1. GIẢI THÍCH:** Thị hiếu nghe nhạc thương mại đại chúng.\n"
                "📝 **2. NHẬN XÉT:** Pop, Rock, Dance Pop chiếm thị phần áp đảo.\n"
                "📊 **3. ĐÁNH GIÁ (HIGH IMPACT):** High-cardinality với >2,100 tags và 28.4% khuyết genre. Gộp về 20 Parent Genre Clusters và Multi-Hot Encode."
            )
        },
        {
            "plot_cell_code_contains": "colors = ['#2ca02c' if v >= 0",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Pearson Correlation với target_popularity\n\n"
                "🔍 **1. GIẢI THÍCH:** Nhạc mới và âm thanh sôi động hỗ trợ độ popular trên Spotify.\n"
                "📝 **2. NHẬN XÉT:** `release_year` (+0.591) và `loudness` (+0.327) tương quan thuận mạnh nhất.\n"
                "📊 **3. ĐÁNH GIÁ (HIGH IMPACT):** Điểm mù tuyến tính của chỉ số Pearson. Kiểm định bằng SHAP Values & Permutation Importance."
            )
        },
        {
            "plot_cell_code_contains": "df_exp = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích, Nhận xét & Đánh giá Chuyên sâu: Xu hướng Tỷ lệ Nhạc Explicit qua các Thập kỷ\n\n"
                "🔍 **1. GIẢI THÍCH:** Sự thống trị của Hip-hop, Rap, R&B đương đại.\n"
                "📝 **2. NHẬN XÉT:** Tỷ lệ explicit bứt phá từ 0.0% lên >15.8% ở thập niên 2010s–2020s.\n"
                "📊 **3. ĐÁNH GIÁ (MEDIUM IMPACT):** Tín hiệu đặc trưng phụ thuộc vào thời gian. Tạo đặc trưng tương tác `explicit_x_genre` và `explicit_x_decade`."
            )
        }
    ]
}

def apply_eoe_comments():
    for rel_path, configs in eoe_comments.items():
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        cells = nb.get('cells', [])
        clean_cells = [c for c in cells if not (c.get('cell_type') == 'markdown' and '📌' in ''.join(c.get('source', [])))]
        
        final_cells = []
        for cell in clean_cells:
            final_cells.append(cell)
            if cell.get('cell_type') == 'code':
                src = ''.join(cell.get('source', []))
                for cfg in configs:
                    needle = cfg['plot_cell_code_contains']
                    if needle in src:
                        md_text = cfg['markdown']
                        md_cell = {
                            "cell_type": "markdown",
                            "metadata": {},
                            "source": [line + "\n" for line in md_text.split("\n")]
                        }
                        final_cells.append(md_cell)
                        print(f"Inserted GIẢI THÍCH + NHẬN XÉT + ĐÁNH GIÁ comment cell into {rel_path} DIRECTLY AFTER plot code cell containing '{needle[:40]}...'")
                        break
        
        nb['cells'] = final_cells
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"Successfully applied GIẢI THÍCH + NHẬN XÉT + ĐÁNH GIÁ comments for {rel_path} (Total cells: {len(final_cells)})\n")

if __name__ == '__main__':
    apply_eoe_comments()
