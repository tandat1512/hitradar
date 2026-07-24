import os
import json

base_dir = r"e:\Dự án 1 hitrada\hitradar\3.NOTEBOOKS"

# Ultra-deep expert commentary updates for all notebooks
deep_updates = {
    r"3.4.eda\01_dataset_overview.ipynb": {
        "inserts": [
            {
                "after_cell_index": 5,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Biểu đồ Quy mô & Kiến trúc Views\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Biểu đồ tổng quan phản ánh quy mô dữ liệu khổng lồ với **586,001 bản ghi bài hát thô**, quản lý 81,776 nghệ sĩ và hơn 2,000 thể loại âm nhạc độc lập trong PostgreSQL. "
                    "Sự chênh lệch cấu trúc giữa `vw_tracks_overview` và `vw_ml_training_dataset` là minh chứng cho bước tiền xử lý nghiêm ngặt: 100% các cột định danh dạng văn bản (`name`, `artists`, `id_artists`) "
                    "và các cột có nguy cơ gây rò rỉ thông tin (Data Leakage) đều đã bị loại bỏ ở view ML. Tỷ lệ giá trị thiếu (Missing Values) đạt mức lý tưởng <0.05%, khẳng định tính nhất quán và toàn vẹn của quy trình ETL đầu vào.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Việc lưu trữ tách biệt giữa View Phân tích (`vw_tracks_overview` giữ lại Metadata để phục vụ BI Dashboard) và View Học Máy (`vw_ml_training_dataset` rút gọn dạng số để phục vụ Vectorization) tuân thủ chặt chẽ nguyên tắc thiết kế Data Warehouse hiện đại. "
                    "Điều này giúp tối ưu hóa bộ nhớ RAM khi huấn luyện mô hình và ngăn chặn tình trạng thuật toán bị 'học vẹt' tên bài hát thay vì học bản chất đặc trưng âm thanh.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Cần tiến hành kiểm toán ngữ nghĩa (Semantic Leakage Audit) trên tất cả các thuộc tính đầu vào. Khuyến nghị tạo bộ kiểm thử kiểm định tĩnh (Static Schema Validation Gate) để đảm bảo không có thuộc tính rò rỉ nào vô tình lọt vào đường ống huấn luyện mô hình (Training Pipeline)."
                )
            },
            {
                "after_cell_index": 12,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bổ Mẫu theo Thập kỷ\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phân bố dữ liệu theo trục thời gian cho thấy hiện tượng lệch mẫu nghiêm trọng (Temporal Imbalance): Thập niên 1990s (108,875 tracks - 18.56%) và 2010s (105,245 tracks - 17.94%) chiếm tổng cộng tới **36.5% toàn bộ dữ liệu**. "
                    "Ngược lại, giai đoạn lịch sử 1920s–1940s chỉ chiếm dưới 5% dung lượng mẫu. Độ nhọn (Kurtosis) và độ lệch (Skewness) theo năm phát hành cho thấy dữ liệu mật độ cao tập trung vào kỷ nguyên số hóa.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Thống kê này phản ánh lịch sử số hóa ngành công nghiệp âm thanh: các bản thu âm trước những năm 1950 bị giới hạn bởi thiết bị thu cơ học cũ và chưa được các nhà đĩa số hóa đầy đủ lên nền tảng Spotify. "
                    "Sự bùng nổ bài hát ở thập niên 1990s và 2010s gắn liền với sự ra đời của nhạc định dạng MP3, Internet và các phần mềm thu âm kỹ thuật số (DAW).\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Rủi ro lớn nhất là mô hình ML bị 'overfitting' vào thẩm mỹ âm nhạc hiện đại và bỏ qua quy luật của nhạc cổ điển. Bắt buộc phải triển khai thuật toán chia tập dữ liệu theo mốc thời gian (**Temporal Stratified Split** hoặc **Time Series Split**) thay vì Random Split để đánh giá chính xác khả năng tổng quát hóa (Generalization Error) của mô hình."
                )
            }
        ]
    },
    r"3.4.eda\02_popularity_analysis.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bố Nhãn Popularity (Right-Skewed & Zero-Inflation)\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phân tích nhãn mục tiêu `target_popularity` ghi nhận chỉ số Skewness dương cao (+0.84) và phân bố bị **lệch phải nặng (Right-Skewed)** với hiện tượng Zero-Inflation rõ nét. "
                    "Nhóm Popularity từ 0 đến 20 chiếm tỷ trọng áp đảo **37.5%** (219,988 tracks), trong đó riêng giá trị Popularity bằng 0 tuyệt đối chiếm **7.6% (44,690 tracks)**. Trung vị (Median = 34.0) thấp hơn đáng kể so với Giá trị Trung bình (Mean = 36.4), khẳng định sự tồn tại của vùng đuôi dài (Heavy Low Tail).\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Điểm Popularity của Spotify được tính toán dựa trên số lượt stream gần đây và tốc độ tăng trưởng lượt nghe (Stream Velocity). 37.5% bài hát ở nhóm đáy phản ánh thực tế ngành công nghiệp âm nhạc: hàng triệu bài hát indie, nhạc thiền, hiệu ứng âm thanh hoặc nội dung tự xuất bản không tiếp cận được thuật toán gợi ý (Recommendation Algorithm) và có lượt stream gần như bằng 0.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Nếu sử dụng hàm mất mát MSE (Mean Squared Error) trên mô hình Linear Regression tiêu chuẩn, mô hình sẽ bị kéo lệch dự báo về phía nhóm giá trị thấp và suy giảm độ chính xác ở phân khúc bài hát Hit (Popularity > 70). "
                    "Đề xuất áp dụng kỹ thuật biến đổi nhãn **Log1p Transformation** hoặc chuyển bài toán sang kiến trúc hai giai đoạn (**Two-Stage Architecture**): Giai đoạn 1 phân loại Binary (Popular vs Zero/Unpopular), Giai đoạn 2 hồi quy (Regression) trên tập Popular bằng thuật toán XGBoost/LightGBM với **Huber Loss / Quantile Loss**."
                )
            },
            {
                "after_cell_index": 7,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bố Popularity theo Trục Thời gian\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Điểm Popularity trung bình thể hiện tương quan thuận đơn điệu (Monotonic Positive Trend) với mốc thời gian phát hành: Thập niên 1920s chỉ đạt trung bình 12.4 điểm, 1960s đạt 32.1 điểm, và bứt phá mạnh mẽ lên **48.6 điểm (2010s)** và **54.2 điểm (2020s)**. "
                    "Độ lệch chuẩn (Std Dev) của Popularity ở các thập kỷ cũ cao hơn hẳn do sự phân hóa giữa các bản nhạc kinh điển duy trì lượt nghe và phần còn lại bị lãng quên.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Thuật toán tính điểm Popularity của Spotify có yếu tố suy giảm theo thời gian (Time Decay Factor), tự động ưu tiên các ca khúc phát hành gần đây do thói quen nghe nhạc của người dùng đại chúng luôn hướng về thị hiếu mới. Các ca khúc thập niên 1960–1980 chỉ đạt điểm cao nếu đó là các bản Hit bất hủ (Evergreen Hits) còn lưu lại trong các Playlist huyền thoại.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Thuộc tính `release_year` đóng vai trò là một 'Super Feature' kiểm soát phần lớn phương sai của Popularity. Nếu không xử lý cẩn thận, mô hình sẽ mặc định phán đoán các bài hát mới là bài Hit. Đề xuất xây dựng đặc trưng chuẩn hóa thời gian **Decade-Normalized Popularity Target** (`popularity - avg_popularity_of_decade`) để giúp mô hình học được giá trị cốt lõi của bản thân bài hát thay vì phụ thuộc vào năm phát hành."
                )
            }
        ]
    },
    r"3.4.eda\03_audio_features_distribution.ipynb": {
        "inserts": [
            {
                "after_cell_index": 5,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bố 7 Thuộc tính Âm thanh (Audio Features)\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phân tích dạng phân bố của 7 thuộc tính âm thanh thể hiện sự phân hóa đa dạng: `danceability` (Mean=0.564, Std=0.166) và `valence` (Mean=0.552, Std=0.257) thể hiện phân bố chuẩn xấp xỉ (Gaussian-like Distribution). "
                    "Trái lại, `speechiness` (Skewness > +2.5, Mean=0.104) và `instrumentalness` (Skewness > +3.1, >65% giá trị xấp xỉ 0.0) bị lệch phải cực đoan với hiện tượng Zero-Inflation nặng. Chỉ số `energy` sở hữu độ phân giải cao nhất (Mean=0.542, Std=0.252) bao phủ trọn vẹn không gian [0, 1].\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "`danceability` và `valence` đại diện cho nhịp điệu và sắc thái cảm xúc âm nhạc chung của đại chúng (Pop/Dance), do đó có phân bố cân bằng. `speechiness` cao chỉ xuất hiện ở nhạc Rap/Podcast, trong khi `instrumentalness` cao chỉ xuất hiện ở nhạc cổ điển/không lời — đây là hai nhóm nhạc chiếm tỷ lệ thiểu số trong kho nhạc thương mại Spotify.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Sự chênh lệch về dải biến thiên và dạng phân bố sẽ làm các thuật toán học máy dựa trên khoảng cách (KNN, SVM, Neural Networks) bị suy giảm hiệu năng. Bắt buộc áp dụng **MinMax Scaling** cho nhóm phân bố chuẩn và biến đổi **Yeo-Johnson / Power Transformation** cho nhóm lệch cực đoan (`speechiness`, `instrumentalness`, `liveness`)."
                )
            },
            {
                "after_cell_index": 7,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Cuộc cách mạng Âm thanh qua 100 năm\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Đồ thị chuỗi thời gian thể hiện sự đảo chiều lịch sử giữa các thuộc tính âm thanh: `acousticness` suy giảm liên tục từ mốc áp đảo **0.88 (năm 1920)** xuống mốc đáy **0.21 (năm 2020)**. Ngược lại, `energy` tăng trưởng từ **0.25 lên 0.68** và `loudness` tăng từ **−18 dB lên −6.5 dB**. Chỉ số `danceability` duy trì xu hướng tăng nhẹ ổn định từ 0.48 lên 0.62.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Sự chuyển dịch này phản ánh chính xác lịch sử công nghệ âm thanh: Chuyển từ thu âm mộc bằng micro đơn thời kỳ 1920s sang âm thanh khuếch đại điện tử (Guitar điện, Synthesizer) ở thập niên 1970s, và sự thống trị của nhạc điện tử (EDM/Pop Synthesizer) cùng kỹ thuật nén âm lượng (Loudness War) trong thập niên 2000s–2010s.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Sự biến đổi xu hướng âm thanh theo thời gian khẳng định các thuộc tính âm thanh không đứng độc lập mà có sự tương tác chặt chẽ với yếu tố thời gian. Khuyến nghị khởi tạo các đặc trưng tương tác **Feature Crosses** (ví dụ: `energy_x_release_year`, `acousticness_ratio_by_decade`) để giúp các thuật toán cây quyết định (XGBoost/LightGBM) bắt được các mối quan hệ phi tuyến tính phức tạp này."
                )
            }
        ]
    },
    r"3.4.eda\04_time_decade_trends.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Mật độ Mẫu & Mất cân bằng Thời gian\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Biểu đồ phân bố số lượng bản ghi chỉ ra hiện tượng thưa thớt dữ liệu (Data Sparsity) ở giai đoạn lịch sử và bùng nổ mật độ mẫu ở giai đoạn hiện đại. Hai thập niên 1990s và 2010s đóng góp lần lượt 108,875 tracks (18.56%) và 105,245 tracks (17.94%). Trong khi đó, giai đoạn 1920s chỉ có 7,610 tracks (~1.30%), tạo nên khoảng chênh lệch mật độ dữ liệu lên tới **14.3 lần**.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Nguyên nhân đến từ quy trình đưa bản ghi lên Spotify: Các đại lý phân phối nhạc số (Distributors) tập trung phát hành toàn bộ kho nhạc thương mại từ kỷ nguyên đĩa CD (1990s) và nhạc số trực tuyến (2010s). Kho nhạc trước 1950 bị thất lạc hoặc vướng bản quyền bản thu cổ.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Mất cân bằng dung lượng mẫu theo thập kỷ sẽ làm suy giảm năng lực dự báo trên tập dữ liệu lịch sử. Khuyến nghị áp dụng kỹ thuật **Stratified Sampling theo Thập kỷ** khi phân chia tập Validation/Test và thiết lập trọng số mẫu (Sample Weights) ngược tỷ lệ dung lượng thập kỷ khi huấn luyện mô hình ML."
                )
            },
            {
                "after_cell_index": 6,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Sự trỗi dậy của Nhạc Explicit\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Tỷ lệ bài hát gán nhãn `explicit` thể hiện mức tăng trưởng đột biến: Giai đoạn 1920s–1970s tỷ lệ này duy trì ở mức xấp xỉ **0.0%**. Từ thập niên 1990s, nhãn explicit bắt đầu tăng lên 5.2% và bứt phá mạnh mẽ đạt đỉnh **>15.8% trong thập niên 2010s và 2020s**.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Sự gia tăng nhạc explicit phản ánh sự chuyển dịch văn hóa đại chúng với sự thống trị của Hip-hop, Rap, R&B đương đại và sự thay đổi trong quy chuẩn kiểm duyệt hệ thống nhãn Parental Advisory (PAL). Ngôn từ cá tính và chủ đề tự do trở thành công thức tạo bản Hit cho thế hệ Gen Z và Millennials.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Biến nhị phân `explicit` là một tín hiệu đầu vào (Feature Signal) mạnh mẽ nhưng mang tính phụ thuộc thời gian (Time-dependent Feature). Cần tạo đặc trưng tương tác **`explicit_x_genre`** và **`explicit_x_decade`** để phản ánh đúng tác động của nhãn này lên độ phổ biến trong từng bối cảnh dòng nhạc."
                )
            },
            {
                "after_cell_index": 8,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Sự Thu hẹp Thời lượng Bài hát Số\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Thời lượng bài hát trung bình ghi nhận biến động qua 3 chu kỳ: Giai đoạn 1920–1950 ổn định ở 3.2–3.5 phút; Giai đoạn 1960–2000 đạt đỉnh 4.3–4.6 phút (độ lệch chuẩn mở rộng do các bản nhạc Progressive Rock/Symphony dài >10 phút); Từ 2015–2020, thời lượng giảm dốc đứng xuống **dưới 3.2 phút (192,000 ms)**.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Sự thu hẹp thời lượng nhạc hiện đại chịu tác động trực tiếp từ nền kinh tế Streaming (Streaming Economy): Spotify tính 1 lượt stream hợp lệ sau 30 giây phát nhạc. Các bài hát ngắn (2.5 - 3.0 phút) giúp tối ưu hóa lượt nghe trên Playlist và tăng doanh thu bản quyền, kết hợp với ảnh hưởng của các nền tảng video ngắn (TikTok/Reels).\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Thời lượng bài hát thô (`duration_ms`) nếu không được chuẩn hóa theo năm phát hành sẽ gây nhầm lẫn cho mô hình. Đề xuất xây dựng đặc trưng tỷ lệ **`duration_to_decade_avg_ratio`** để đo lường độ dài bài hát tương đối so với chuẩn mực của cùng thời kỳ."
                )
            }
        ]
    },
    r"3.4.eda\05_artist_genre_analysis.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Top Nghệ sĩ theo Số lượng Bản ghi & Long-Tail Bias\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Biểu đồ top nghệ sĩ ghi nhận hai thực thể áp đảo: *'Die drei ???'* (3,856 tracks) và *'Lata Mangeshkar'* (2,605 tracks). Trong tổng số 81,776 nghệ sĩ, phân bố số lượng bài hát thể hiện đặc tính **đuôi dài cực đoan (Extreme Long-Tail)** với >68% nghệ sĩ chỉ sở hữu từ 1 đến 2 bài hát.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Kết quả này hé lộ hiện tượng nén dữ liệu nội dung thoại (Audio Drama/Spoken Word) của series kịch trinh thám Đức và kho nhạc đồ sộ của huyền thoại nhạc phim Bollywood. Kho nhạc thô của Spotify chứa cả nội dung phi âm nhạc thương mại, đòi hỏi quy trình lọc dữ liệu khắt khe.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Nếu đưa `artist_id` trực tiếp vào mô hình bằng kỹ thuật One-Hot Encoding sẽ làm bùng nổ chiều dữ liệu (Curse of Dimensionality) với >80K cột thưa. Đề xuất áp dụng **Target Encoding kèm Smoothing Factor** hoặc rút gọn thành các chỉ số thống kê nghệ sĩ (`artist_track_count`, `artist_historical_avg_popularity`)."
                )
            },
            {
                "after_cell_index": 6,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Top Nghệ sĩ theo Popularity Trung bình\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Top các nghệ sĩ có điểm Popularity trung bình cao nhất đạt mức ấn tượng từ **82.5 đến 89.4 điểm**, quy tụ các ngôi sao toàn cầu như Bad Bunny, Taylor Swift, Drake, BTS, The Weeknd. Đáng chú ý, các nghệ sĩ này có số lượng tracks trung bình trong dataset ở mức vừa phải (50–300 bài).\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Sự phân hóa giữa Top Track Count và Top Popularity khẳng định nguyên lý: **Quy mô danh mục nhạc không tỷ lệ thuận với độ phổ biến**. Các nghệ sĩ Pop mainstream sở hữu chiến lược phát hành bài hát tập trung, ngân sách marketing khổng lồ và lượng fan hâm mộ trung thành tạo nên lượt stream liên tục.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Điểm danh tiếng nghệ sĩ là một tín hiệu dự báo Popularity cực mạnh nhưng có nguy cơ rò rỉ dữ liệu tương lai (Data Leakage). Khi tính toán đặc trưng nghệ sĩ (`artist_mean_popularity`), bắt buộc chỉ được tính toán trên tập **Train Set** (hoặc dùng Out-of-Fold Target Encoding) để tránh rò rỉ thông tin sang Validation/Test Set."
                )
            },
            {
                "after_cell_index": 8,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bố Thể loại Âm nhạc (Genre High-Cardinality)\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phân tích thể loại ghi nhận hơn **2,100 genre tags** chi tiết trong cơ sở dữ liệu. Nhóm Top Genres chiếm thị phần lớn nhất gồm Pop, Rock, Dance Pop, Rap và Indie. Tuy nhiên, có tới **28.4% nghệ sĩ** bị khuyết thông tin thể loại (Empty Genre Array).\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Thể loại nhạc trên Spotify mang bản chất Đa nhãn (Multi-label) và có tính chất phân cấp phức tạp (gồm Main Genre và Sub-genre dạng Niche). Nhiều thẻ thể loại được tạo tự động bởi thuật toán phân loại khiến dữ liệu có độ nhiễu cao.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Tình trạng High-Cardinality và thiếu dữ liệu ở Genre đòi hỏi quy trình tiền xử lý phải thực hiện chuẩn hóa: Gộp các sub-genre chi tiết về **20 Parent Genre Clusters** chính, gán nhãn `unknown_genre` cho các giá trị thiếu và áp dụng kỹ thuật **Multi-Hot Encoding** hoặc **Genre Embeddings**."
                )
            }
        ]
    },
    r"3.4.eda\06_correlation_outlier_analysis.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Ma trận Tương quan Tuyến tính Pearson\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Hệ số tương quan Pearson giữa 10 đặc trưng số và `target_popularity` chỉ ra 3 nhân tố tác động thuận hàng đầu: `release_year` (**+0.591** - Tương quan mạnh), `loudness` (**+0.327** - Tương quan trung bình) và `energy` (**+0.302**). Ngược lại, 2 nhân tố tác động nghịch mạnh nhất là `acousticness` (**−0.371**) và `instrumentalness` (**−0.237**). Các biến `speechiness`, `liveness` và `duration_min` có hệ số tương quan xấp xỉ 0.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Kết quả phân tích tương quan phản ánh chính xác thị hiếu nghe nhạc thương mại đại chúng trên Spotify: Nhạc mới, âm thanh to rõ, sôi động có khả năng thành bài Hit cao hơn hẳn nhạc mộc hoặc nhạc không lời.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Hệ số tương quan tuyến tính Pearson không phản ánh được các mối quan hệ phi tuyến. Sự thống trị của `release_year` (+0.591) đặt ra yêu cầu phải đánh giá độ quan trọng của đặc trưng (Feature Importance) thông qua cả chỉ số **SHAP Values** và **Permutation Importance** sau khi huấn luyện mô hình phi tuyến."
                )
            },
            {
                "after_cell_index": 6,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Mối quan hệ Phi tuyến (Non-linear Binned Scatter)\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phương pháp Binned Scatter Plot (gom nhóm theo bin và tính Popularity trung bình) hé lộ cấu trúc phi tuyến rõ nét: Mối quan hệ giữa `loudness` và Popularity thể hiện đường cong bão hòa (Saturated Curve) — tăng nhanh từ −30 dB đến −5 dB, sau đó đi ngang và suy giảm nhẹ khi loudness > 0 dB. `acousticness` giảm điểm phi tuyến tính mạnh mẽ ngay khi vượt ngưỡng 0.35.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Ngưỡng bão hòa của `loudness` giải thích cho giới hạn chịu đựng thính giác của người nghe: Nhạc quá nhỏ khó nghe trên tai nghe di động, nhưng nhạc quá nén (Over-compressed/Clipping > 0dB) sẽ gây mệt mỏi thính giác (Ear Fatigue) dẫn đến giảm lượt nghe duy trì.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Cấu trúc phi tuyến tính rõ ràng này khẳng định các mô hình tuyến tính (Linear/Ridge Regression) sẽ bị hạn chế năng lực biểu diễn nghiêm trọng. Bắt buộc ưu tiên sử dụng các thuật toán **Gradient Boosted Trees (XGBoost, LightGBM, CatBoost)** vốn có khả năng tự động phân tách ngưỡng (Splitting Thresholds) trên các đường cong bão hòa này."
                )
            },
            {
                "after_cell_index": 9,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân tích Ngoại lệ Thời lượng Bài hát (`duration_ms`)\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phân tích outlier thời lượng xác định 2 nhóm dị biệt cực đoan: Nhóm bài quá ngắn (<10 giây) gồm **26 tracks**; Nhóm bài quá dài (>60 phút) gồm **83 tracks**. Mặc dù tỷ lệ dị biệt cực thấp (<0.02% toàn bộ dataset), dải biến thiên thời lượng kéo dài từ 1.2 giây đến 5.4 giờ.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Nhóm <10s thường là các hiệu ứng âm thanh (Sound Effects/DJ Intros) hoặc lỗi metadata thu âm. Nhóm >60 phút là các podcast, bản thu âm thiền/tiếng mưa rơi hoặc album tổng hợp (Non-standard Tracks).\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Các điểm dữ liệu dị biệt thời lượng cực đoan này sẽ tạo ra khoảng khoảng cách Euclidean lớn và tính toán Gradient lỗi lớn khi huấn luyện mô hình ML. Khuyến nghị quy tắc làm sạch: Loại bỏ hoàn toàn các bản ghi có duration < 10 giây và áp dụng kỹ thuật **Winsorization / Clipping** đưa các bài hát >20 phút (1,200,000 ms) về ngưỡng trần cố định."
                )
            }
        ]
    },
    r"3.1.hieu_du_lieu\01_data_understanding.ipynb": {
        "inserts": [
            {
                "after_cell_index": 5,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Quy mô Dataset & Kiến trúc Views PostgreSQL\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Biểu đồ quy mô tổng quan quản lý 586,001 bản ghi thô với cấu trúc view phân tách giữa phân tích tổng quan (`vw_tracks_overview`) và dữ liệu cho học máy (`vw_ml_training_dataset`). Cột định danh chữ đã bị bóc tách 100%.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Đảm bảo nguyên tắc cách ly dữ liệu huấn luyện và ngăn ngừa rò rỉ thông tin tên bài hát/nghệ sĩ vào thuật toán dự báo.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Thực hiện kiểm thử tự động Schema Gate trên toàn bộ các thuộc tính nạp vào pipeline huấn luyện."
                )
            },
            {
                "after_cell_index": 14,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bố nhãn Popularity & Zero-Inflation\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Phân bố lệch phải nặng với 37.5% bài hát ở phân khúc 0–20 điểm và 7.6% bài hát đạt điểm 0 tuyệt đối.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Phản ánh lượng lớn nội dung indie/podcast không có lượt stream trên nền tảng Spotify.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Áp dụng Log1p transformation hoặc kiến trúc hai giai đoạn Two-Stage Classification + Regression."
                )
            },
            {
                "after_cell_index": 21,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Phân bố 7 Audio Features & Xu hướng Đa biến\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "Sự phân hóa giữa nhóm chuẩn (`danceability`, `valence`) và nhóm lệch cực đoan (`speechiness`, `instrumentalness`).\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Minh họa lịch sử chuyển dịch từ nhạc mộc 1920s (`acousticness` > 0.8) sang nhạc điện tử hiện đại (`energy` > 0.65, `loudness` > −7 dB).\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Áp dụng MinMax Scaling và Yeo-Johnson Transformation cho toàn bộ đặc trưng âm thanh."
                )
            },
            {
                "after_cell_index": 29,
                "markdown": (
                    "### 📌 Giải thích & Đánh giá Chuyên sâu Ma trận Tương quan Pearson & Tính Phi tuyến\n\n"
                    "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                    "`release_year` (+0.591) và `loudness` (+0.327) đóng vai trò tác động dương mạnh nhất.\n\n"
                    "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                    "Người nghe trực tuyến ưu tiên bài hát mới và âm thanh sôi động.\n\n"
                    "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                    "Ưu tiên sử dụng Gradient Boosted Decision Trees (XGBoost/LightGBM) để nắm bắt điểm bão hòa phi tuyến."
                )
            }
        ]
    }
}

def apply_deep_notebook_updates():
    for rel_path, config in deep_updates.items():
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        # Filter out old 📌 comment cells to replace with new deep 3-part comments
        new_cells = []
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'markdown' and '📌' in ''.join(cell.get('source', [])):
                continue # remove old simple comment cell
            new_cells.append(cell)
        
        inserts = config.get('inserts', [])
        inserts_sorted = sorted(inserts, key=lambda x: x['after_cell_index'], reverse=True)
        
        for ins in inserts_sorted:
            idx = ins['after_cell_index']
            md_text = ins['markdown']
            new_cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + "\n" for line in md_text.split("\n")]
            }
            insert_at = min(idx + 1, len(new_cells))
            new_cells.insert(insert_at, new_cell)
        
        nb['cells'] = new_cells
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"Successfully upgraded notebook with expert 3-part analysis: {rel_path} (Total cells: {len(new_cells)})")

if __name__ == '__main__':
    apply_deep_notebook_updates()
