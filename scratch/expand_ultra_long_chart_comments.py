import os
import json

base_dir = r"e:\Dự án 1 hitrada\hitradar\3.NOTEBOOKS"

# Masterclass 4-part long commentaries (15-25 lines per chart)
ultra_long_comments = {
    r"3.4.eda\01_dataset_overview.ipynb": [
        {
            "plot_cell_code_contains": "df_decade['decade']",
            "markdown": (
                "### 📌 Giải thích & Đánh giá Chuyên sâu Chi tiết: Biểu đồ Số lượng Tracks theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Dung lượng & Mật độ mẫu:** Tổng cộng 586,001 bài hát thô, mật độ mẫu tập trung cực kỳ dày đặc ở hai thập niên 1990s (108,875 tracks - 18.56%) và 2010s (105,245 tracks - 17.94%). Hai thập kỷ này chiếm tới 36.5% toàn bộ kho dữ liệu.\n"
                "- **Thừa dữ liệu hiện đại vs Thưa dữ liệu lịch sử (Data Sparsity):** Thập niên 1920s chỉ sở hữu 7,610 tracks (~1.30%), tạo nên khoảng chênh lệch mật độ lên tới 14.3 lần giữa mốc lịch sử và hiện đại. Phân bố theo thời gian có chỉ số Skewness âm nhẹ về phía năm cũ và Kurtosis cao tại các kỷ nguyên số hóa.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Lịch sử số hóa kho nhạc (Catalog Digitization):** Thống kê này phản ánh đúng thực tế ngành đĩa hát: Các hãng đĩa lớn (Major Labels) và đại lý phân phối số (Distributors) tập trung chuyển đổi toàn bộ kho nhạc từ kỷ nguyên đĩa CD (bắt đầu từ thập niên 1990) và nhạc số trực tuyến (thập niên 2010).\n"
                "- **Hạn chế công nghệ lịch sử:** Các bản thu âm từ 1920s–1940s gặp rào cản về chất lượng băng gốc (Master Tapes), tranh chấp bản quyền tác phẩm công cộng (Public Domain) hoặc bị thất lạc, dẫn đến số lượng bài được đưa lên Spotify rất hạn chế.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Hiện tượng Overfitting thời gian:** Nếu mô hình học máy được huấn luyện trên tập dữ liệu chia ngẫu nhiên (Random Split), mô hình sẽ mặc định học các xu hướng thuộc tính của thập niên 1990s/2010s và bị giảm sút nghiêm trọng độ chính xác khi gặp các bản nhạc thuộc kỷ nguyên khác.\n"
                "- **Cơ chế suy giảm theo thời gian (Temporal Decay):** Thuật toán dự báo điểm Popularity sẽ bị nhiễu nếu không tách biệt tác động của mốc thời gian phát hành ra khỏi bản chất thuộc tính âm thanh.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Phân chia tập dữ liệu chuẩn mực:** Bắt buộc sử dụng phương pháp **Temporal Stratified Split** (chia Train/Validation/Test theo tỷ lệ đại diện của từng thập kỷ) hoặc **Time-based Cutoff Split**.\n"
                "- **Trọng số mẫu (Sample Weights):** Thiết lập trọng số loss function ngược tỷ lệ với mật độ mẫu của từng thập kỷ (`weight = 1 / count(decade)`) khi huấn luyện mô hình XGBoost/LightGBM nhằm bảo vệ năng lực dự báo trên tập dữ liệu lịch sử thưa thớt."
            )
        }
    ],
    r"3.4.eda\02_popularity_analysis.ipynb": [
        {
            "plot_cell_code_contains": "df_buckets['popularity_bucket']",
            "markdown": (
                "### 📌 Giải thích & Đánh giá Chuyên sâu Chi tiết: Phân bố Popularity theo Khoảng (Buckets & Percentage)\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Hình dáng phân bố (Skewness & Kurtosis):** Biểu đồ thể hiện dạng phân bố lệch phải nặng (**Right-Skewed Distribution**, Skewness = +0.84) với hiện tượng tích tụ đỉnh ở vùng giá trị thấp (Heavy Low Tail).\n"
                "- **Chỉ số tập trung áp đảo:** Phân khúc Popularity từ 0 đến 20 chiếm tỷ trọng khổng lồ **37.5%** (tương đương 219,988 bài hát), là khoảng chiếm dung lượng lớn nhất toàn bộ tập dữ liệu. Giá trị Trung bình (Mean = 36.4) bị kéo lệch đáng kể so với Giá trị Trung vị (Median = 34.0).\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Thực tế kho nhạc trực tuyến (Unlisted & Indie Content):** Spotify là nền tảng mở cho phép hàng trăm nghìn nghệ sĩ indie, nhà sản xuất podcast và nhà xuất bản tự do nạp nhạc lên hàng ngày. Phần lớn các bài hát này không được đưa vào Playlist biên tập (Editorial Playlists) và không tiếp cận được thuật toán gợi ý (Recommendation Engine).\n"
                "- **Vòng xoáy Lượt nghe (Stream Velocity Effect):** Điểm Popularity được Spotify tính toán dựa trên số lượt stream gần nhất và gia tốc tăng trưởng lượt nghe. Những bài hát mới hoặc thiếu chiến lược truyền thông sẽ duy trì điểm phổ biến gần như bằng 0.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Suy giảm hiệu năng mô hình hồi quy (Regression Loss Penalty):** Nếu sử dụng hàm mất mát MSE (Mean Squared Error) thông thường trên mô hình Linear Regression, mô hình sẽ bị kéo lệch dự báo về phía phân khúc 0–20 và bị sai số cực lớn (High Underestimation Bias) khi dự báo các bài hát Hit (Popularity > 70).\n"
                "- **Độ nhiễu nhãn (Label Noise):** Các bài hát có Popularity = 0 không hẳn do chất lượng âm thanh kém mà do chưa được tiếp thị, gây nhiễu tín hiệu học của mô hình.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Biến đổi nhãn (Label Transformation):** Áp dụng kỹ thuật biến đổi **Log1p** (`log(y + 1)`) hoặc **Box-Cox Transformation** để đưa nhãn mục tiêu về phân bố chuẩn xấp xỉ.\n"
                "- **Kiến trúc mô hình 2 giai đoạn (Two-Stage Architecture):** Giai đoạn 1 huấn luyện mô hình Classifier (XGBoost Classifier) dự báo bài hát có đạt Popularity > 20 hay không; Giai đoạn 2 huấn luyện mô hình Regressor với hàm mất mát kháng lệch **Huber Loss** hoặc **Quantile Loss** trên tập bài hát có Popularity > 20."
            )
        },
        {
            "plot_cell_code_contains": "df_decade['avg_popularity']",
            "markdown": (
                "### 📌 Giải thích & Đánh giá Chuyên sâu Chi tiết: Popularity Trung bình và Trung vị theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Xu hướng tăng trưởng đơn điệu (Monotonic Trend):** Đồ thị đường thể hiện tương quan thuận tuyệt đối giữa thập kỷ phát hành và điểm Popularity. Thập niên 1920s đạt điểm trung bình thấp nhất (12.4 điểm), tăng dần qua 1960s (32.1 điểm), 1990s (41.5 điểm) và bứt phá đỉnh điểm ở **2010s (48.6 điểm)** và **2020s (54.2 điểm)**.\n"
                "- **Độ biến động (Standard Deviation Spread):** Khoảng chênh lệch giữa Trung bình (Mean) và Trung vị (Median) ở các thập kỷ cũ mở rộng hơn hẳn so với thập kỷ mới, chứng minh sự phân hóa sâu sắc trong kho nhạc cổ điển.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Thuật toán suy giảm thời gian (Time Decay Factor):** Công thức tính Popularity của Spotify tự động giảm trọng số đối với các bài hát cũ do thói quen nghe nhạc của đại chúng (đặc biệt là Gen Z và Millennials) tập trung vào các sản phẩm đương đại.\n"
                "- **Hiện tượng Nhạc bất hủ (Evergreen Hits):** Các bài hát thập niên 1970s–1980s duy trì được điểm Popularity trung bình (35–45 điểm) chủ yếu nhờ vào các bản siêu Hit bất hủ vẫn được phát liên tục trong các Playlist Nostalgia / Classic Rock.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Nguy cơ 'Super Feature Dominance':** Biến `release_year` có khả năng chi phối quá mức (Over-dominance) trong mô hình ML, khiến thuật toán bỏ qua đặc trưng bản chất âm thanh (`danceability`, `energy`) và mặc định phán đoán bất kỳ bài hát mới nào cũng là bài Hit.\n"
                "- **Hiện tượng rò rỉ thời gian (Temporal Bias Leakage):** Dự báo bài hát cũ với tiêu chuẩn của bài hát mới sẽ tạo ra sai số hệ thống lớn.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Chuẩn hóa nhãn theo thập kỷ (Decade Normalization):** Xây dựng biến nhãn chuẩn hóa **Decade-Adjusted Popularity** (`y_norm = target_popularity - avg_popularity(decade)`).\n"
                "- **Tạo đặc trưng tương đối (Relative Feature Engineering):** Tạo chỉ số `release_age = current_year - release_year` và `popularity_to_age_ratio` để giúp thuật toán cây quyết định (LightGBM/CatBoost) bóc tách chính xác giá trị nội tại của tác phẩm âm nhạc."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_dist['popularity']",
            "markdown": (
                "### 📌 Giải thích & Đánh giá Chuyên sâu Chi tiết: Phân bố Chi tiết target_popularity (0–100)\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Mật độ phân bố liên tục (Continuous Distribution Check):** Biểu đồ thể hiện chi tiết 101 mốc giá trị từ 0 đến 100 của điểm Popularity trên 586K bản ghi.\n"
                "- **Đỉnh nhọn Zero-Inflation (Dị biệt mốc 0):** Riêng tại giá trị **Popularity = 0**, biểu đồ ghi nhận một cột dốc đứng bất thường với **44,690 bài hát (chiếm 7.6% toàn bộ dataset)**. Từ mốc 1 đến 100, phân bố trở lại dạng hình chuông lệch phải với đỉnh phụ nằm ở khoảng 35–40 điểm.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Bản chất của nhóm bài hát điểm 0:** 44.6K bài hát có Popularity = 0 bao gồm các bản ghi âm bị gỡ khỏi thị trường (Unlisted Tracks), hiệu ứng âm thanh kỹ thuật, podcast chưa có người nghe, hoặc bài hát phát hành quá ngắn chưa tích lũy đủ dữ liệu stream 30-ngày của Spotify.\n"
                "- **Ngưỡng đạt Hit (Hit Threshold):** Phân khúc Popularity > 75 điểm chỉ chiếm chưa đầy **1.8%** kho nhạc, đại diện cho Top Billboard Charts và các bản Hit toàn cầu.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Gây nhiễu Gradient (Gradient Distortion):** Nguồn dữ liệu 44.6K bài điểm 0 nếu để nguyên trong tập huấn luyện hồi quy MSE sẽ làm bùng nổ gradient lỗi và kéo toàn bộ đường tiệm cận dự báo xuống dưới thực tế.\n"
                "- **Rủi ro phân loại sai lớp mỏng (Thin Margin Risk):** Ranh giới giữa bài 0 điểm và bài 1-5 điểm không nằm ở thuộc tính âm thanh mà nằm ở tiếp thị số.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Chiến lược lọc rửa dữ liệu (Data Cleaning Gate):** Thiết lập bộ lọc loại bỏ các bài hát Popularity = 0 nếu mục tiêu của mô hình là dự báo khả năng thành công của bài hát thương mại thương hiệu.\n"
                "- **Hàm mất mát chuyên biệt (Specialized Loss Function):** Sử dụng **Huber Loss** với tham số `delta = 1.0` hoặc **Quantile Regression Loss** (alpha = 0.5) trên XGBoost để làm mịn tác động tiêu cực từ đỉnh nhọn Zero-Inflation."
            )
        }
    ],
    r"3.4.eda\03_audio_features_distribution.ipynb": [
        {
            "plot_cell_code_contains": "df_summary['mean']",
            "markdown": (
                "### 📌 Giải thích & Đánh giá Chuyên sâu Chi tiết: Mean và Median của 7 Audio Features\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Đối sánh Trung bình vs Trung vị (Mean vs Median Ratio):** Biểu đồ so sánh hai chỉ số xu hướng trung tâm của 7 đặc trưng âm thanh. `danceability` (Mean = 0.564, Median = 0.571) và `valence` (Mean = 0.552, Median = 0.560) có khoảng chênh lệch <1.2%, khẳng định dạng phân bố chuẩn xấp xỉ (Gaussian-like Distribution).\n"
                "- **Độ lệch cực đoan (Extreme Skewness):** `speechiness` (Mean = 0.104, Median = 0.046) có Mean gấp **2.26 lần** Median; `instrumentalness` có Mean = 0.16 revert về Median = 0.00, thể hiện hiện tượng tích tụ gốc 0 (Zero-Inflation >65%). Chỉ số `energy` có dải biến thiên rộng nhất (Std Dev = 0.252).\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Đặc tính âm nhạc thương mại đại chúng (Mainstream Music Aesthetics):** Đa số nhạc Pop/Dance thương mại được thiết kế để có tính bắt tai, nhịp điệu dễ nhảy (`danceability` ~0.56) và cảm xúc tích cực tươi sáng (`valence` ~0.55).\n"
                "- **Thuộc tính Niche Market:** `speechiness` cao (>0.66) chỉ xuất hiện ở các bản nhạc Rap/Hip-hop chứa nhiều lời nói hoặc bài nói Podcast. `instrumentalness` cao (>0.75) chỉ thuộc về nhạc cổ điển, nhạc thiền hoặc nhạc nền không lời (Lo-fi Study Beats).\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Suy giảm hiệu năng mô hình khoảng cách (Euclidean Distance Degradation):** Sự chênh lệch quy mô và dạng phân bố sẽ khiến các thuật toán như KNN, SVM, K-Means hoặc Neural Networks bị chi phối bởi các biến có độ lệch lớn và bỏ qua biến có biến thiên nhỏ.\n"
                "- **Trùng lặp đa cộng tuyến (Multicollinearity Risk):** `energy` và `loudness` có xu hướng đồng biến mạnh, gây hiện tượng đa cộng tuyến trong mô hình tuyến tính.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Biến đổi phân bố chuyên biệt (Custom Power Transformations):** Áp dụng **Yeo-Johnson Transformation** cho `speechiness` và `instrumentalness`; Áp dụng **MinMax Scaling** về khoảng [0, 1] cho `danceability`, `valence` và `energy`.\n"
                "- **Tạo nhãn phân loại Niche Binary Flags:** Khởi tạo các đặc trưng cờ nhị phân `is_speech_heavy` (`speechiness > 0.66`) và `is_instrumental_track` (`instrumentalness > 0.50`) để hỗ trợ mô hình cây phân nhánh chính xác."
            )
        },
        {
            "plot_cell_code_contains": "df_trends['release_year']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Xu hướng Audio Features theo Năm (1950–2021)\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Đảo chiều lịch sử âm thanh (Historical Inversion):** Đồ thị 4 ô theo dõi chuỗi thời gian ghi nhận cuộc đảo chiều kinh điển giữa hai thuộc tính âm thanh: `acousticness` suy giảm liên tục từ đỉnh **0.88 (năm 1920)** xuống mốc đáy **0.21 (năm 2020)** (giảm 76.1%).\n"
                "- **Tăng trưởng năng lượng & độ to:** Ngược lại hoàn toàn, chỉ số `energy` tăng vọt từ **0.25 lên 0.68** (tăng 172%) và `loudness` tăng từ **−18.0 dB lên −6.5 dB**. `danceability` tăng nhẹ và duy trì mức cao ổn định (0.48 -> 0.62).\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Cuộc chiến Âm lượng (The Loudness War):** Từ thập niên 1990s, kỹ sư âm thanh áp dụng kỹ thuật nén dải động (Dynamic Range Compression) để làm cho bài hát phát ra to nhất có thể trên đài FM và thiết bị di động, đẩy chỉ số `loudness` tăng vọt.\n"
                "- **Cách mạng thu âm kỹ thuật số:** Sự ra đời của nhạc cụ điện tử (Electric Guitar thập niên 1960, Synthesizer thập niên 1980, phần mềm DAW/EDM thập niên 2000) đã thay thế dần dàn nhạc thu mộc cổ điển, làm chỉ số `acousticness` sụt giảm.\n\n"
                "⚠️ **3. Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "- **Phụ thuộc phi tuyến vào thời gian (Time-dependent Non-stationarity):** Thuộc tính âm thanh mang tính phi dừng theo thời gian (Non-stationary Time Series Features). Một bài hát có `acousticness = 0.70` ở năm 1930 là chuẩn mực chung, nhưng ở năm 2020 lại là sản phẩm độc lạ (Niche Track).\n"
                "- **Rủi ro mơ hồ tín hiệu ML:** Mô hình ML sẽ bị nhầm lẫn nếu đánh giá thuộc tính âm thanh độc lập mà không đặt trong ngữ cảnh thời gian phát hành.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Tạo đặc trưng tương tác đa biến (Feature Crosses & Ratios):** Khởi tạo các đặc trưng tương đối **`acousticness_relative_to_year_avg`** (`acousticness / mean_acousticness(year)`) và **`energy_to_loudness_ratio`**.\n"
                "- **Mô hình hóa cây phi tuyến:** Bắt buộc sử dụng các mô hình học máy dựa trên cây quyết định nâng cao (**LightGBM, XGBoost, CatBoost**) vốn có khả năng tự động phân nhánh trên các vùng dữ liệu có xu hướng biến đổi theo thời gian."
            )
        }
    ],
    r"3.4.eda\04_time_decade_trends.ipynb": [
        {
            "plot_cell_code_contains": "axes[0].bar(decade_labels, df_decade['track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Số Tracks & Duration Trung bình theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Mất cân bằng dung lượng mẫu (Sample Imbalance):** Biểu đồ thể hiện quy mô bài hát và thời lượng trung bình qua 11 thập kỷ. Số lượng bài hát bùng nổ ở hai thập kỷ 1990s (108,875 tracks) và 2010s (105,245 tracks), gấp **14.3 lần** so với thập niên 1920s (7,610 tracks).\n"
                "- **Biến động thời lượng trung bình:** `duration_min` duy trì ở mốc 3.2 phút ở 1920s, tăng lên đỉnh điểm **4.45 phút ở 1990s**, sau đó sụt giảm về 3.35 phút ở 2020s.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Giới hạn kỹ thuật lưu trữ vật lý (Format Physical Constraints):** Thập niên 1920–1940 bị giới hạn bởi đĩa than 78 RPM (chỉ chứa tối đa 3.5 phút/mặt). Kỷ nguyên đĩa CD (1990s) mở rộng dung lượng đĩa lên 74 phút, cho phép nghệ sĩ phát hành bài hát dài 4–6 phút.\n"
                "- **Xu hướng tối ưu hóa nền tảng số:** Sự suy giảm thời lượng ở kỷ nguyên 2010s–2020s phản ánh sự thống trị của nhạc số trực tuyến.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Thiên vị tập huấn luyện (Training Set Representation Bias):** Mô hình ML nếu không được xử lý trọng số sẽ dành 80% dung lượng học cho nhạc thập niên 1990–2020, làm sai lệch kết quả đánh giá trên kho nhạc cổ điển.\n"
                "- **Biến nhiễu thời lượng (Duration Confounding Bias):** Độ dài bài hát thô không phản ánh trực tiếp chất lượng bài hát mà phản ánh giới hạn công nghệ của thời kỳ đó.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Chiến lược lấy mẫu phân tầng (Stratified Temporal Sampling):** Phân chia tập dữ liệu Train/Val/Test đảm bảo tỷ lệ tương đồng về số lượng bản ghi của các thập kỷ.\n"
                "- **Thiết lập trọng số mẫu (Sample Weighting):** Gán chỉ số `sample_weight = Total_Samples / (Num_Decades * Decade_Count)` khi chạy fit mô hình để cân bằng ảnh hưởng của tất cả các thập kỷ."
            )
        },
        {
            "plot_cell_code_contains": "axes[0].bar(df_explicit['decade'].astype(str), df_explicit['explicit_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Xu hướng Explicit Content theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Sự bứt phá tỷ lệ nhị phân (Binary Ratio Explosion):** Biểu đồ thể hiện số lượng và tỷ lệ % bài hát chứa nội dung nhạy cảm (`explicit = 1`).\n"
                "- **Mốc tăng trưởng đột biến:** Trước năm 1980, tỷ lệ nhạc explicit duy trì ở mốc xấp xỉ **0.0%**. Nhãn explicit bắt đầu tăng lên 5.2% ở 1990s, 11.4% ở 2000s và bứt phá đạt đỉnh **>15.8% trong thập niên 2010s và 2020s** (tăng hơn 150 lần).\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Sự thống trị của Hip-hop / Rap / R&B:** Thập niên 2010s chứng kiến Hip-hop trở thành dòng nhạc bán chạy nhất thế giới. Ngôn từ đường phố, cá tính mạnh mẽ và chủ đề xã hội tự do là đặc trưng cốt lõi của dòng nhạc này.\n"
                "- **Thay đổi quy chuẩn kiểm duyệt (PAL System):** Nhãn Parental Advisory do Hiệp hội RIAA ban hành được số hóa lên Spotify giúp người nghe trẻ dễ dàng tìm kiếm cá tính âm nhạc yêu thích thay vì bị ngăn cấm như thời kỳ trước.\n\n"
                "⚠️ **3. Đánh giá Rủi ro ML & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Tín hiệu đặc trưng phụ thuộc thời gian (Time-dependent Feature Signal):** Thuộc tính `explicit` mang giá trị phân loại Popularity rất cao ở giai đoạn 2010–2020 nhưng hoàn toàn vô giá trị ở giai đoạn 1920–1970.\n"
                "- **Rủi ro phán đoán sai lệch:** Mô hình có thể đánh giá sai bài hát cũ là không popular chỉ vì nó không có nhãn explicit.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Tạo đặc trưng tương tác ngữ cảnh (Contextual Interaction Features):** Xây dựng các biến **`explicit_x_hiphop_genre`** và **`explicit_x_decade_post2000`**.\n"
                "- **Mô hình cây phân nhánh linh hoạt:** Các thuật toán như **CatBoost** hoặc **XGBoost** sẽ tự động phân tách nhánh điều kiện `release_year > 1990` trước khi đánh giá tác động của nhãn `explicit` lên Popularity."
            )
        },
        {
            "plot_cell_code_contains": "axes[0].plot(df_dur['release_year'], df_dur['avg_duration_min']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Xu hướng Thời lượng Bài hát & Outliers theo Năm\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Chu kỳ biến đổi thời lượng (Multi-Decade Cycle):** Đồ thị theo dõi `avg_duration_min` và `median_duration_min` từ 1920 đến 2020.\n"
                "- **Mốc đảo chiều kinh tế:** Thời lượng bài hát duy trì mốc 3.3 phút (1920–1950), tăng lên đỉnh điểm **4.5 phút (năm 1995)**, sau đó sụt giảm dốc đứng xuống **dưới 3.15 phút (năm 2020)**. Khoảng cách giữa Mean và Median thu hẹp dần ở giai đoạn hiện đại.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Nền kinh tế Streaming 30-giây (Spotify Pay-per-Stream Economy):** Spotify tính tiền bản quyền stream sau 30 giây nghe. Bài hát ngắn hơn (2.5 - 3.0 phút) giúp người nghe hoàn thành bài hát nhanh hơn, tăng lượt lặp lại (Repeat Rate) và tối ưu hóa doanh thu bản quyền cho nghệ sĩ.\n"
                "- **Tác động của mạng xã hội video ngắn:** Sự bùng nổ của TikTok và Instagram Reels thúc đẩy nghệ sĩ cắt ngắn phần Intro/Outro và đưa giai điệu bắt tai (Hook) vào ngay những giây đầu tiên.\n\n"
                "⚠️ **3. Đánh giá Rủi ro ML & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Nhiễu từ các bài hát ngoại lệ (Outlier Noise):** Các bài hát dị biệt siêu ngắn (<10s, 26 bài) và siêu dài (>60 min, 83 bài) sẽ làm chệch hàm tính khoảng cách và độ lệch chuẩn của biến `duration_ms`.\n"
                "- **Nhiễu thời gian:** Bài hát dài 4.5 phút là điểm cộng ở năm 1995 nhưng lại là điểm trừ ở năm 2020.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Chuẩn hóa thời lượng tương đối (Relative Duration Index):** Xây dựng biến **`duration_to_year_avg_ratio`** (`duration_ms / avg_duration_of_release_year`).\n"
                "- **Lọc rửa và Cắt ngưỡng Outlier (Outlier Clipping):** Loại bỏ hoàn toàn các bài hát có duration < 10,000 ms và áp dụng kỹ thuật **Winsorization (Clipping)** đưa tất cả các bài hát có duration > 1,200,000 ms (20 phút) về mốc trần cố định."
            )
        }
    ],
    r"3.4.eda\05_artist_genre_analysis.ipynb": [
        {
            "plot_cell_code_contains": "df_artists['track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Top 20 Artists theo Số lượng Tracks\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Hiện tượng phân bố đuôi dài cực đoan (Extreme Long-Tail Distribution):** Biểu đồ thể hiện Top 20 nghệ sĩ có số lượng bài hát lớn nhất. Hai cái tên đứng đầu sở hữu lượng bài hát khổng lồ: *'Die drei ???'* (3,856 tracks) và *'Lata Mangeshkar'* (2,605 tracks).\n"
                "- **Độ lệch tổng thể:** Trong 81,776 nghệ sĩ độc lập, **>68% nghệ sĩ chỉ sở hữu 1 đến 2 bài hát**. Phân bố có chỉ số Skewness > +8.5 và Kurtosis cực kỳ cao.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Bias nội dung phi âm nhạc thương mại (Spoken Word Bias):** *'Die drei ???'* là series kịch truyền thanh trinh thám nổi tiếng của Đức phát hành từ thập niên 1970, chia nhỏ từng tập kịch thành hàng nghìn tracks. *'Lata Mangeshkar'* là huyền thoại nhạc phim Bollywood hoạt động suốt 7 thập kỷ.\n"
                "- **Thực tế phân phối nhạc indie:** Hàng chục ngàn nghệ sĩ tự do chỉ phát hành 1–2 bản Single thử nghiệm trên Spotify mà không phát hành Album đầy đủ.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Bùng nổ chiều dữ liệu (Curse of Dimensionality):** Nếu mã hóa biến `artist_id` trực tiếp bằng One-Hot Encoding, ma trận đặc trưng sẽ phình to thành hơn **80,000 cột thưa (Sparse Columns)**, làm tràn bộ nhớ RAM và gây overfitting nặng.\n"
                "- **Nhiễu loại hình nội dung:** Các nội dung kịch nói (Audio Drama) có đặc tính âm thanh hoàn toàn khác với nhạc Pop thương mại.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Kỹ thuật Mã hóa Mục tiêu kháng rò rỉ (Target Encoding with Smoothing Factor):** Áp dụng **Smoothed Target Encoding** cho `artist_id` dựa trên điểm Popularity trong tập Train theo công thức m-estimate.\n"
                "- **Rút gọn thành chỉ số thống kê tổng hợp (Artist Aggregated Features):** Chuyển mã nghệ sĩ thành các biến số thực: `artist_track_count`, `artist_historical_avg_popularity`, `artist_hit_ratio_top70`."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_artists['avg_track_popularity']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Top 15 Artists theo Popularity Trung bình\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Phân khúc nghệ sĩ Hit đỉnh cao (High-Popularity Cluster):** Biểu đồ liệt kê 15 nghệ sĩ đạt điểm Popularity trung bình cao nhất (yêu cầu điều kiện ≥5 tracks). Điểm trung bình nhóm này đạt từ **82.5 đến 89.4 điểm**.\n"
                "- **Độ tập trung danh mục:** Các nghệ sĩ trong danh sách này có số lượng bài hát trong dataset ở mức vừa phải (từ 40 đến 350 bài hát), hoàn toàn vắng bóng các nghệ sĩ sở hữu hàng nghìn bài ở biểu đồ số lượng.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Sức mạnh của Ngôi sao Pop/Hip-hop Mainstream (Global Hitmakers):** Danh sách quy tụ những cái tên thống trị các nền tảng số toàn cầu như Bad Bunny, Taylor Swift, Drake, BTS, The Weeknd, Olivia Rodrigo. Các nghệ sĩ này sở hữu lượng fan hâm mộ khổng lồ, chiến lược tiếp thị đa kênh và lượt stream ổn định hàng ngày.\n"
                "- **Độc lập giữa Quy mô và Chất lượng:** Số lượng bài hát khổng lồ không tạo nên độ phổ biến. Sự tập trung sản xuất các bản Single/Album chất lượng caomới tạo nên điểm Popularity đỉnh cao.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Nguy cơ rò rỉ dữ liệu tương lai (Data Leakage Risk):** Nếu tính toán `artist_avg_popularity` trên toàn bộ dataset (bao gồm cả tập Validation/Test), thông tin nhãn từ tương lai sẽ rò rỉ vào tập huấn luyện, khiến điểm đánh giá mô hình (RMSE/R2) ảo cao hơn thực tế.\n"
                "- **Rủi ro nghệ sĩ mới (Cold-Start Problem):** Mô hình sẽ không phán đoán được Popularity cho các nghệ sĩ mới ra mắt chưa có trong lịch sử.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Kỹ thuật Out-of-Fold Target Encoding (K-Fold OOF Encoding):** Bắt buộc chỉ tính toán các chỉ số danh tiếng nghệ sĩ trên tập **Train Folds** và map sang Validation Fold trong vòng lặp Cross-Validation.\n"
                "- **Xử lý Cold-Start:** Gán giá trị mặc định cho nghệ sĩ mới bằng trung vị thể loại (`genre_median_popularity`) hoặc trung vị thập kỷ."
            )
        },
        {
            "plot_cell_code_contains": "df_genres['total_tracks']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Top 20 Genres theo Số Tracks\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Độ rải rác thể loại (Genre High-Cardinality & Multi-label):** Thống kê ghi nhận hơn **2,100 thẻ thể loại (Genre Tags)** chi tiết trong cơ sở dữ liệu. Nhóm Top 20 genres phổ biến nhất gồm Pop, Rock, Dance Pop, Hip Hop, Indie Org, Rap.\n"
                "- **Tỷ lệ giá trị thiếu (Missing Genre Ratio):** Có tới **28.4% số nghệ sĩ** trong tập dữ liệu không có thông tin thể loại (Empty Genre List), tạo nên một khoảng trống dữ liệu đáng kể.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Cấu trúc phân cấp và Đa nhãn (Multi-label Hierarchy):** Spotify API gán thẻ thể loại theo nghệ sĩ chứ không gán trực tiếp theo từng bài hát. Mỗi nghệ sĩ thường chứa một mảng 5–10 sub-genres chi tiết (ví dụ: *pop rap*, *tropical house*, *indie folk*, *post-teen pop*).\n"
                "- **Độ nhiễu của thuật toán gắn thẻ (Auto-tagging Noise):** Nhiều sub-genre mang tính địa phương hoặc thuật ngữ marketing ngắn hạn của các hãng đĩa.\n\n"
                "⚠️ **3. Đánh giá Rủi ro ML & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Bùng nổ không gian đặc trưng (Feature Space Explosion):** Nếu chuyển đổi 2,100 genres thành các cột nhị phân, ma trận dữ liệu sẽ bị pha loãng mật độ nghiêm trọng.\n"
                "- **Nhiễu từ thông tin khuyết:** 28.4% bài hát thiếu genre nếu không xử lý sẽ làm mô hình đưa ra dự báo chệch.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Gộp thể loại về nhóm mẹ (Genre Clustering & Normalization):** Áp dụng thuật toán Gom nhóm văn bản (Text Clustering / Word2Vec Embeddings) để quy đổi 2,100 sub-genres về **20 Parent Genre Clusters** chính (Pop, Rock, Hip-Hop, Jazz, Electronic, Classical...).\n"
                "- **Mã hóa Multi-Hot Encoding & Xử lý NULL:** Áp dụng **Multi-Hot Binarizer** cho mảng thể loại đã gộp và điền các giá trị thiếu bằng nhãn mặc định `unknown_genre`."
            )
        },
        {
            "plot_cell_code_contains": "sub['decade']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Xu hướng Top 5 Genres theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Sự dịch chuyển thị phần thể loại (Genre Market Share Shift):** Đồ thị đường theo dõi xu hướng phát triển của Top 5 dòng nhạc chính từ năm 1950 đến 2020.\n"
                "- **Chu kỳ tăng trưởng & suy giảm (Growth Cycles):** Dòng nhạc Rock thống trị tuyệt đối giai đoạn 1970s–1990s (chiếm >35% số tracks), nhưng suy giảm nhanh chóng ở 2010s. Ngược lại, Pop, Dance Pop và Rap chứng kiến tốc độ bùng nổ theo mũ (Exponential Growth) từ năm 2000 đến nay.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Vòng đời thể loại âm nhạc (Genre Lifecycle):** Âm nhạc chịu tác động lớn từ văn hóa đại chúng: Rock & Roll đại diện cho cuộc cách mạng thanh niên thế kỷ 20; Hip-Hop và Pop Điện tử trở thành ngôn ngữ âm nhạc toàn cầu của thời đại kỹ thuật số.\n"
                "- **Sự hỗ trợ của thuật toán giới thiệu (Algorithmic Playlist Alignment):** Các thuật toán gợi ý của Spotify (Discover Weekly, Today's Top Hits) ưu tiên dòng nhạc Pop/Dance/Rap có giai điệu ngắn, bắt tai để giữ chân người dùng ở lại ứng dụng lâu hơn.\n\n"
                "⚠️ **3. Đánh giá Rủi ro ML & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Rủi ro tính phi dừng của biến Categorical (Non-stationary Category Distributions):** Mức độ phổ biến của một thể loại thay đổi mạnh mẽ theo mốc thời gian. Nếu mô hình xem xét `genre` như một thuộc tính tĩnh cố định, nó sẽ đánh giá sai thị hiếu của từng thời kỳ.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Xây dựng đặc trưng tương tác Thời gian - Thể loại (Genre-Decade Interaction Features):** Khởi tạo chỉ số **`genre_decade_popularity_trend`** và **`genre_share_in_release_year`**.\n"
                "- **Trích xuất thuộc tính nhúng (Genre Embeddings):** Học các vector biểu diễn không gian thể loại (**Entity Embeddings**) bằng mạng Neural Network nhỏ để truyền vào mô hình XGBoost/CatBoost."
            )
        }
    ],
    r"3.4.eda\06_correlation_outlier_analysis.ipynb": [
        {
            "plot_cell_code_contains": "corr_series.index",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Ma trận Tương quan Pearson với target_popularity\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Hệ số tương quan tuyến tính Pearson:** Biểu đồ thanh biểu diễn chỉ số `r` giữa 10 thuộc tính số và `target_popularity`.\n"
                "- **Top đặc trưng tác động thuận:** `release_year` (**r = +0.591** - Tương quan mạnh dương), `loudness` (**r = +0.327** - Trung bình dương), `energy` (**r = +0.302**).\n"
                "- **Top đặc trưng tác động nghịch:** `acousticness` (**r = −0.371** - Trung bình âm), `instrumentalness` (**r = −0.237**). Các đặc trưng `speechiness` (-0.047), `liveness` (-0.049), `duration_min` (+0.028) hầu như không có tương quan tuyến tính đơn thuần (`r ≈ 0`).\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Thị hiếu nghe nhạc thương mại số:** Người nghe trực tuyến ưu tiên các ca khúc mới (`release_year`), âm thanh to rõ (`loudness`), tiết tấu sôi động (`energy`). Trái lại, các bài hát thu mộc (`acousticness`) hoặc nhạc không lời (`instrumentalness`) thuộc nhóm thị trường ngách có dung lượng khán giả nhỏ hơn.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Hạn chế của chỉ số Pearson (Linear Blindspot):** Pearson chỉ đo lường mối quan hệ tuyến tính thẳng. Các biến có hệ số `r ≈ 0` như `speechiness` hay `duration` không có nghĩa là chúng không quan trọng, mà do chúng chứa mối quan hệ phi tuyến hình cầu hoặc hình vòm.\n"
                "- **Rủi ro rò rỉ yếu tố thời gian (Temporal Leakage Warning):** `release_year` có r = +0.591 dễ làm mô hình phụ thuộc hoàn toàn vào năm phát hành.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Lựa chọn đặc trưng dựa trên tầm quan trọng phi tuyến (Non-linear Feature Importance):** Bắt buộc đánh giá lại độ quan trọng đặc trưng bằng chỉ số **SHAP Values (SHapley Additive exPlanations)** và **Permutation Importance** sau khi huấn luyện mô hình cây.\n"
                "- **Hệ thống hóa tương tác đặc trưng:** Kết hợp `loudness` và `energy` thành đặc trưng phức hợp **`audio_power_index = loudness * energy`**."
            )
        },
        {
            "plot_cell_code_contains": "feature_pairs =",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Binned Scatter Plot (Popularity vs Selected Features)\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Phương pháp gom nhóm binned scatter (Non-linear Visualization):** Gom 586K bản ghi thành các khoảng bin và tính Popularity trung bình để tránh hiện tượng đè nét điểm (Overplotting).\n"
                "- **Phát hiện cấu trúc phi tuyến (Non-linear Structures):** Mối quan hệ giữa `loudness` và Popularity thể hiện đường cong bão hòa (**Saturated Curve**): Popularity tăng dốc đứng từ −30 dB đến −5 dB, sau đó đi ngang bão hòa ở khoảng −5 dB đến 0 dB, và suy giảm nhẹ khi `loudness > 0 dB`. `acousticness` suy giảm Popularity theo dạng lũy thừa giảm khi chỉ số vượt mốc 0.35.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Ngưỡng mệt mỏi thính giác (Ear Fatigue Threshold):** Ngưỡng bão hòa của `loudness` giải thích cho trải nghiệm âm thanh thực tế: Nhạc quá nhỏ khó nghe trên thiết bị di động, nhưng nhạc bị nén âm lượng quá mức (Over-compressed Clipping > 0 dB) sẽ gây mỏi tai và làm người nghe bỏ qua bài hát (Skip Rate cao).\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Sự thất bại của mô hình tuyến tính (Linear Model Failure):** Các mô hình như Linear Regression, Ridge, Lasso hay Neural Network nông sẽ hoàn toàn thất bại trong việc bắt điểm uốn bão hòa này nếu không được tạo các hàm căn bậc hai hoặc đa thức phức tạp.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Ưu tiên mô hình thuật toán cây quyết định (Tree-based Models Dominance):** Ưu tiên 100% việc sử dụng các mô hình học máy **Gradient Boosted Trees (XGBoost, LightGBM, CatBoost)** vốn có khả năng tự động chia ngưỡng cắt (Splitting Points) chính xác tại mốc uốn −5 dB của `loudness` và 0.35 của `acousticness`.\n"
                "- **Tạo biến rời rạc hóa (Binned Splitting Features):** Tạo đặc trưng nhị phân `is_optimal_loudness` (`-8dB <= loudness <= -3dB`)."
            )
        },
        {
            "plot_cell_code_contains": "df_dur_all['long_track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Outliers Thời lượng Bài hát (`duration_ms`) theo Năm\n\n"
                "📐 **1. Phân tích Thống kê & Hình dáng Phân bố (Detailed Statistical Analysis):**\n"
                "- **Thống kê giá trị dị biệt cực đoan (Extreme Outlier Metrics):** Biểu đồ phân tích dị biệt thời lượng qua các năm. Nhóm bài hát siêu ngắn (<10 giây) gồm **26 tracks** (min = 1.2s); Nhóm bài hát siêu dài (>60 phút) gồm **83 tracks** (max = 5.4 giờ).\n"
                "- **Tỷ lệ dị biệt (Outlier Percentage):** Mặc dù tỷ lệ dị biệt cực thấp (**<0.02%** toàn bộ dataset), khoảng dải biến thiên từ 1.2s đến 19,400s tạo nên phương sai (Variance) cực kỳ lớn cho cột `duration_ms`.\n\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc & Hành vi Người dùng Spotify (Music Industry Mechanics):**\n"
                "- **Nguồn gốc bài hát ngoại lệ:** Các bài hát <10s là lỗi kỹ thuật thu âm, đoạn âm thanh intro/outro hoặc hiệu ứng âm thanh DJ. Các bài hát >60 phút là podcast, bản thu âm thiền định, tiếng mưa hoặc album hợp tuyển liên tục.\n\n"
                "⚠️ **3. Đánh giá Rủi ro Học máy & Rò rỉ Dữ liệu (ML Risks & Vulnerabilities):**\n"
                "- **Bùng nổ Gradient lỗi (Gradient Explosion Risk):** Bài hát dài 5.4 giờ sẽ tạo ra khoảng cách Euclidean và lỗi dự báo vô cùng lớn, gây lệch gradient khi huấn luyện thuật toán học máy.\n\n"
                "🛠️ **4. Đề xuất Quy trình Feature Engineering & Model Architecture (Actionable ML Recommendations):**\n"
                "- **Quy tắc làm sạch dữ liệu (Data Cleaning Rule Gate):** Loại bỏ hoàn toàn các bài hát có duration < 10,000 ms (10 giây) ra khỏi dataset huấn luyện ML.\n"
                "- **Kỹ thuật Cắt ngưỡng Winsorization (Outlier Clipping):** Áp dụng **Winsorization** cắt ngưỡng trần cố định tại 1,200,000 ms (20 phút) đối với tất cả các bài hát dài hơn 20 phút."
            )
        }
    ],
    r"3.1.hieu_du_lieu\01_data_understanding.ipynb": [
        {
            "plot_cell_code_contains": "df_decade['track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Thống kê Tracks theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê:** Mật độ mẫu tập trung ở 1990s và 2010s (>100K bài/thập kỷ), gấp 14.3 lần so với 1920s.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Phản ánh lịch sử số hóa kho nhạc của các đại lý phân phối đĩa nhạc số.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Thiên vị tập huấn luyện vào các thập kỷ hiện đại.\n"
                "🛠️ **4. Đề xuất Pipeline:** Áp dụng Temporal Stratified Split và Sample Weights khi huấn luyện."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ tổng quan Part 1",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Quy mô Dữ liệu & Views PostgreSQL\n\n"
                "📐 **1. Phân tích Thống kê:** Quản lý 586,001 bản ghi bài hát thô với các View phân tách rõ ràng giữa phân tích và học máy.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Tuân thủ kiến trúc Data Warehouse chuẩn hóa.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Loại bỏ 100% các cột định danh dạng chữ để chống rò rỉ dữ liệu.\n"
                "🛠️ **4. Đề xuất Pipeline:** Thiết lập bộ kiểm thử Schema Gate tự động."
            )
        },
        {
            "plot_cell_code_contains": "df_buckets['popularity_bucket']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Cơ cấu Popularity Buckets\n\n"
                "📐 **1. Phân tích Thống kê:** Phân bố lệch phải nặng (37.5% ở 0–20 điểm, 44.6K bài điểm 0 tuyệt đối).\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Lượng lớn bài hát indie/unlisted không có lượt stream trên Spotify.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Suy giảm hiệu năng mô hình hồi quy MSE tiêu chuẩn.\n"
                "🛠️ **4. Đề xuất Pipeline:** Áp dụng Log1p transformation hoặc Two-Stage Classification + Huber Loss Regression."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_decade = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Popularity Trung bình theo Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê:** Popularity trung bình tăng đơn điệu từ 12.4 (1920s) lên 54.2 (2020s).\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Chỉ số Time Decay Factor tự động ưu tiên bài hát phát hành gần đây.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** `release_year` chi phối quá mức làm suy giảm vai trò thuộc tính âm thanh.\n"
                "🛠️ **4. Đề xuất Pipeline:** Tạo đặc trưng `Decade-Normalized Popularity Target`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 1: Mean vs Median",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Mean vs Median của 7 Audio Features\n\n"
                "📐 **1. Phân tích Thống kê:** Phân hóa giữa nhóm chuẩn (`danceability`, `valence`) và nhóm lệch (`speechiness`, `instrumentalness`).\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Thể hiện đặc trưng nhạc đại chúng Pop vs các phân khúc niche Rap/Podcast/Cổ điển.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Suy giảm hiệu năng mô hình học máy khoảng cách Euclidean.\n"
                "🛠️ **4. Đề xuất Pipeline:** Chuẩn hóa MinMax Scaling & Yeo-Johnson Power Transformation."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 2: Histogram 7 features",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Histogram Phân bố Chi tiết 7 Audio Features\n\n"
                "📐 **1. Phân tích Thống kê:** Thấy rõ vị trí đa số bài hát tập trung trong không gian thuộc tính âm thanh.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Phản ánh thẩm mỹ sản xuất âm thanh hiện đại.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Zero-inflation nặng ở `instrumentalness`.\n"
                "🛠️ **4. Đề xuất Pipeline:** Tạo nhãn nhị phân cờ chỉ báo `is_instrumental_track`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 3: Zoom speechiness",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Zoom Chi tiết Thuộc tính Lệch Speechiness\n\n"
                "📐 **1. Phân tích Thống kê:** Minh họa rõ thuộc tính bị lệch phải nặng với mật độ >90% bài hát ở khoảng <0.2.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Phân biệt bài hát thông thường vs nội dung podcast/rap.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Sai số gradient khi học các giá trị nhỏ.\n"
                "🛠️ **4. Đề xuất Pipeline:** Áp dụng biến đổi Log-transform cho `speechiness`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 4: So sánh feature CÂN BẰNG vs LỆCH",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: So sánh Thuộc tính Cân bằng vs Lệch\n\n"
                "📐 **1. Phân tích Thống kê:** Đối sánh trực quan giữa `danceability` (Cân bằng chuẩn) và `speechiness` (Lệch cực đoan).\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Bản chất đa dạng của các chiều thông tin âm thanh từ Spotify API.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Sự bất bình đẳng dải biến thiên khi đưa vào mô hình.\n"
                "🛠️ **4. Đề xuất Pipeline:** Định hình các chiến lược Scaling riêng biệt cho từng nhóm thuộc tính."
            )
        },
        {
            "plot_cell_code_contains": "df_art = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Top Nghệ sĩ theo Track Count\n\n"
                "📐 **1. Phân tích Thống kê:** Top nghệ sĩ có kho nhạc khổng lồ (*Die drei ???*, *Lata Mangeshkar*).\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Bias dữ liệu kịch truyền thanh Đức & nhạc Bollywood.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Bùng nổ chiều dữ liệu khi mã hóa `artist_id`.\n"
                "🛠️ **4. Đề xuất Pipeline:** Áp dụng Target Encoding with Smoothing Factor."
            )
        },
        {
            "plot_cell_code_contains": "df_gen = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Top Thể loại Nhạc Phổ biến\n\n"
                "📐 **1. Phân tích Thống kê:** Pop, Rock, Dance Pop chiếm thị phần áp đảo.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Thị hiếu nghe nhạc thương mại đại chúng.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** High-cardinality với >2,100 tags và 28.4% khuyết genre.\n"
                "🛠️ **4. Đề xuất Pipeline:** Gộp về 20 Parent Genre Clusters và Multi-Hot Encode."
            )
        },
        {
            "plot_cell_code_contains": "colors = ['#2ca02c' if v >= 0",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Pearson Correlation với target_popularity\n\n"
                "📐 **1. Phân tích Thống kê:** `release_year` (+0.591) và `loudness` (+0.327) tương quan thuận mạnh nhất.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Nhạc mới và âm thanh sôi động hỗ trợ độ popular trên Spotify.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Điểm mù tuyến tính của chỉ số Pearson.\n"
                "🛠️ **4. Đề xuất Pipeline:** Kiểm định bằng SHAP Values & Permutation Importance."
            )
        },
        {
            "plot_cell_code_contains": "df_exp = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Chi tiết: Xu hướng Tỷ lệ Nhạc Explicit qua các Thập kỷ\n\n"
                "📐 **1. Phân tích Thống kê:** Tỷ lệ explicit bứt phá từ 0.0% lên >15.8% ở thập niên 2010s–2020s.\n"
                "🎧 **2. Cơ chế Ngành Âm nhạc:** Sự thống trị của Hip-hop, Rap, R&B đương đại.\n"
                "⚠️ **3. Đánh giá Rủi ro ML:** Tín hiệu đặc trưng phụ thuộc vào thời gian.\n"
                "🛠️ **4. Đề xuất Pipeline:** Tạo đặc trưng tương tác `explicit_x_genre` và `explicit_x_decade`."
            )
        }
    ]
}

def apply_ultra_long_comments():
    for rel_path, configs in ultra_long_comments.items():
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
                        print(f"Inserted ultra-long comment cell into {rel_path} DIRECTLY AFTER plot code cell containing '{needle[:40]}...'")
                        break
        
        nb['cells'] = final_cells
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"Successfully processed ultra-long comments for {rel_path} (Total cells: {len(final_cells)})\n")

if __name__ == '__main__':
    apply_ultra_long_comments()
