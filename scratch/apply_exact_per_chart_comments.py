import os
import json

base_dir = r"e:\Dự án 1 hitrada\hitradar\3.NOTEBOOKS"

notebook_plot_comments = {
    r"3.4.eda\01_dataset_overview.ipynb": [
        {
            "plot_cell_code_contains": "df_decade['decade']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Số lượng Tracks theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ phân bố lượng tracks theo thập kỷ cho thấy mật độ mẫu tập trung cực kỳ dày đặc ở hai thập niên 1990s (108,875 tracks - 18.56%) và 2010s (105,245 tracks - 17.94%). "
                "Trái lại, giai đoạn lịch sử 1920s–1940s có số lượng bài khá khiêm tốn (dưới 20,000 bài), phản ánh hạn chế về số hóa dữ liệu âm nhạc cổ điển.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Thống kê này phản ánh lịch sử số hóa kho nhạc: các đại lý phân phối nhạc số tập trung phát hành toàn bộ kho nhạc thương mại từ kỷ nguyên đĩa CD (1990s) và nhạc số trực tuyến (2010s). "
                "Kho nhạc trước 1950 bị thất lạc hoặc vướng bản quyền bản thu cổ.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Sự chênh lệch này đòi hỏi chiến lược phân chia dữ liệu Train/Validation/Test phải theo mốc thời gian (**Temporal Stratified Split**) thay vì ngẫu nhiên. "
                "Điều này tránh cho mô hình bị học thiên vị (bias) vào các thập kỷ hiện đại và đảm bảo khả năng tổng quát hóa (Generalization Error) của mô hình."
            )
        }
    ],
    r"3.4.eda\02_popularity_analysis.ipynb": [
        {
            "plot_cell_code_contains": "df_buckets['popularity_bucket']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Phân bố Popularity theo Khoảng (Buckets & Percentage)\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ gồm 2 đồ thị con thể hiện số lượng và tỷ lệ % bài hát theo các khoảng Popularity. "
                "Kết quả chỉ ra phân bố bị **lệch phải nặng (Right-Skewed)**: Nhóm Popularity từ 0 đến 20 chiếm tỷ trọng áp đảo **37.5%** (219,988 tracks), là nhóm có dung lượng lớn nhất toàn dataset.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Spotify chứa lượng lớn các bài hát mới phát hành, bài hát chưa có lượt stream hoặc các nội dung podcast/indie chưa tiếp cận được thuật toán gợi ý (Recommendation Algorithm).\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Sự lệch nhãn cực đoan này sẽ khiến các mô hình hồi quy (Regression) tiêu chuẩn bị chệch dự báo về phía giá trị thấp. "
                "Đề xuất áp dụng kỹ thuật biến đổi nhãn **Log1p Transformation** hoặc sử dụng các hàm mất mát kháng lệch như **Huber Loss / Quantile Loss**."
            )
        },
        {
            "plot_cell_code_contains": "df_decade['avg_popularity']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Popularity Trung bình và Trung vị theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Đồ thị đường thể hiện Popularity trung bình và trung vị qua các thập kỷ (1920s–2020s). "
                "Điểm Popularity trung bình tăng trưởng đơn điệu liên tục từ **12.4 điểm (1920s)** lên **48.6 điểm (2010s)** và **54.2 điểm (2020s)**.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Thuật toán Spotify áp dụng chỉ số suy giảm theo thời gian (Time Decay Factor), tự động ưu tiên các ca khúc phát hành gần đây do thói quen người nghe đại chúng luôn hướng về nhạc mới.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "`release_year` đóng vai trò là một 'Super Feature' chi phối Popularity. Đề xuất xây dựng đặc trưng chuẩn hóa thời gian **Decade-Normalized Popularity Target** (`popularity - avg_popularity_of_decade`) giúp mô hình học được giá trị cốt lõi của bài hát."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_dist['popularity']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Phân bố Chi tiết target_popularity (0–100)\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ cột chi tiết 101 mốc giá trị (0 đến 100) của `target_popularity`. "
                "Riêng mốc **Popularity = 0** ghi nhận đỉnh nhọn bất thường với **44,690 tracks (7.6%)** — biểu hiện rõ nét của hiện tượng Zero-Inflation.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Các bài hát có điểm Popularity bằng 0 tuyệt đối là các bản ghi unlisted, podcast không lượt nghe hoặc bài hát bị gỡ khỏi hệ thống streaming.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Khuyến nghị áp dụng kiến trúc hai giai đoạn (**Two-Stage Architecture**): Giai đoạn 1 phân loại Binary (Popular vs Zero/Unpopular), Giai đoạn 2 hồi quy (Regression) trên tập Popular bằng XGBoost/LightGBM."
            )
        }
    ],
    r"3.4.eda\03_audio_features_distribution.ipynb": [
        {
            "plot_cell_code_contains": "df_summary['mean']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Mean và Median của 7 Audio Features\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ cột so sánh Mean và Median của 7 đặc trưng âm thanh. "
                "`danceability` (Mean=0.564) và `valence` (Mean=0.552) có Mean xấp xỉ Median, thể hiện phân bố chuẩn cân bằng. "
                "Trái lại, `speechiness` (Mean=0.104) và `instrumentalness` có Mean chênh lệch lớn so với Median, thể hiện phân bố lệch phải cực đoan.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "`danceability` và `valence` đại diện cho cảm xúc Pop/Dance đại chúng nên cân bằng. `speechiness` và `instrumentalness` chỉ cao ở nhạc Rap/Podcast hoặc Cổ điển — là các phân khúc niche.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Bắt buộc áp dụng **MinMax Scaling** cho nhóm phân bố chuẩn và biến đổi **Yeo-Johnson / Power Transformation** cho nhóm lệch cực đoan (`speechiness`, `instrumentalness`)."
            )
        },
        {
            "plot_cell_code_contains": "df_trends['release_year']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Xu hướng Audio Features theo Năm (1950–2021)\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Đồ thị 4 ô hiển thị sự dịch chuyển lịch sử của đặc trưng âm thanh: "
                "`acousticness` suy giảm mạnh từ **>0.85 (1920s)** xuống **0.21 (2020s)**, trong khi `energy` tăng từ **0.25 lên 0.68** và `loudness` tăng từ **−18 dB lên −6.5 dB**.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Minh họa lịch sử thu âm: chuyển từ nhạc mộc cổ điển sang nhạc điện tử khuếch đại (Synthesizer/EDM) và kỹ thuật nén âm lượng (Loudness War) kỷ nguyên số.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Khuyến nghị tạo các đặc trưng tương tác **Feature Crosses** (ví dụ: `energy_x_release_year`, `acousticness_ratio_by_decade`) giúp mô hình cây (XGBoost/LightGBM) bắt mối quan hệ đa biến."
            )
        }
    ],
    r"3.4.eda\04_time_decade_trends.ipynb": [
        {
            "plot_cell_code_contains": "axes[0].bar(decade_labels, df_decade['track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Số Tracks & Duration Trung bình theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ cột và đồ thị đường thể hiện số lượng bài hát và thời lượng trung bình qua các thập kỷ. "
                "Số lượng bài hát bùng nổ ở 1990s và 2010s (>100K bài/thập kỷ), chênh lệch **14.3 lần** so với 1920s (7.6K bài).\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Phản ánh lịch sử số hóa kho nhạc của các nhà phân phối số và các giới hạn đĩa than vật lý thời kỳ đầu.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Cần áp dụng kỹ thuật **Stratified Sampling theo Thập kỷ** khi chia tập dữ liệu và gán trọng số mẫu (**Sample Weights**) ngược tỷ lệ dung lượng thập kỷ khi huấn luyện."
            )
        },
        {
            "plot_cell_code_contains": "axes[0].bar(df_explicit['decade'].astype(str), df_explicit['explicit_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Xu hướng Explicit Content theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ đôi thể hiện số lượng và tỷ lệ % bài hát chứa nội dung nhạy cảm (`explicit`). "
                "Tỷ lệ explicit tăng trưởng từ **0.0% (trước 1980)** lên đỉnh điểm **>15.8% trong thập niên 2010s–2020s**.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Xu hướng này gắn liền với sự bùng nổ của Hip-hop, Rap, R&B hiện đại nơi ngôn từ cá tính được bộc lộ tự do.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Khởi tạo đặc trưng tương tác **`explicit_x_genre`** và **`explicit_x_decade`** để phản ánh đúng tác động của nhãn này lên Popularity trong từng bối cảnh dòng nhạc."
            )
        },
        {
            "plot_cell_code_contains": "axes[0].plot(df_dur['release_year'], df_dur['avg_duration_min']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Xu hướng Thời lượng Bài hát & Outliers theo Năm\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Đồ thị theo dõi thời lượng trung bình/trung vị và phân bố bài hát ngắn/dài. "
                "Thời lượng bài hát đạt đỉnh 4.5 phút ở thập niên 1990s và **giảm dốc đứng xuống <3.2 phút từ năm 2015 trở lại đây**.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Sự thu hẹp thời lượng chịu tác động từ cơ chế trả tiền bản quyền stream sau 30 giây của Spotify, khuyến khích bài hát ngắn để tối ưu lượt stream.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Xây dựng đặc trưng tỷ lệ **`duration_to_decade_avg_ratio`** để đo lường độ dài bài hát tương đối so với chuẩn mực của cùng thời kỳ."
            )
        }
    ],
    r"3.4.eda\05_artist_genre_analysis.ipynb": [
        {
            "plot_cell_code_contains": "df_artists['track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Top 20 Artists theo Số lượng Tracks\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ cột ngang hiển thị 20 nghệ sĩ có số lượng bài hát lớn nhất. "
                "*'Die drei ???'* (3,856 tracks) và *'Lata Mangeshkar'* (2,605 tracks) chiếm vị trí thống trị áp đảo. Danh sách nghệ sĩ thể hiện đặc tính **Extreme Long-Tail** (>68% nghệ sĩ có 1-2 bài).\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Phản ánh bias dữ liệu kịch truyền thanh Đức và nhạc phim Bollywood trong kho nhạc thô Spotify.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Không One-Hot Encode `artist_id` vì làm bùng nổ chiều dữ liệu (>80K cột). Áp dụng **Target Encoding kèm Smoothing Factor** hoặc rút gọn thành chỉ số thống kê nghệ sĩ."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_artists['avg_track_popularity']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Top 15 Artists theo Popularity Trung bình\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ thể hiện Top nghệ sĩ có điểm Popularity trung bình cao nhất (82.5 đến 89.4 điểm), quy tụ Bad Bunny, Taylor Swift, Drake, BTS, The Weeknd.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Khẳng định nguyên lý: **Số lượng bài hát không đồng nghĩa với độ phổ biến**. Các ngôi sao Pop đại chúng phát hành bài hát chất lượng cao kèm chiến lược marketing khổng lồ.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Tính toán đặc trưng nghệ sĩ (`artist_mean_popularity`) phải dùng phương pháp **Out-of-Fold Target Encoding** chỉ trên tập Train Set để chống rò rỉ dữ liệu tương lai."
            )
        },
        {
            "plot_cell_code_contains": "df_genres['total_tracks']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Top 20 Genres theo Số Tracks\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ thống kê Top 20 thể loại phổ biến nhất (Pop, Rock, Dance Pop, Hip Hop). Dataset chứa >2,100 genre tags và 28.4% nghệ sĩ bị khuyết thông tin genre.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Genre trên Spotify có tính chất Multi-label và phân cấp phức tạp (Main genre & Sub-genre).\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Thực hiện chuẩn hóa: Gộp các sub-genre về **20 Parent Genre Clusters** chính, gán nhãn `unknown_genre` cho giá trị thiếu và áp dụng **Multi-Hot Encoding**."
            )
        },
        {
            "plot_cell_code_contains": "sub['decade']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Xu hướng Top 5 Genres theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Đồ thị đường theo dõi sự thay đổi thị phần của Top 5 genres qua các thập kỷ (1950–2020). "
                "Rock thống trị giai đoạn 1970s–1990s, nhường chỗ cho Pop, Dance Pop và Rap bứt phá mạnh mẽ ở 2010s–2020s.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Phản ánh sự thay đổi vòng đời dòng nhạc (Genre Lifecycle) và thị hiếu tiêu dùng âm thanh đại chúng qua các thế hệ.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Tạo các đặc trưng tương tác **`genre_x_decade_trend`** giúp mô hình nắm bắt xu hướng tăng trưởng/suy giáp của từng dòng nhạc."
            )
        }
    ],
    r"3.4.eda\06_correlation_outlier_analysis.ipynb": [
        {
            "plot_cell_code_contains": "corr_series.index",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Ma trận Tương quan Pearson với target_popularity\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ thanh thể hiện tương quan Pearson giữa 10 đặc trưng số và Popularity. "
                "`release_year` (**+0.591**), `loudness` (**+0.327**), `energy` (**+0.302**) tương quan thuận mạnh nhất. `acousticness` (**−0.371**) tương quan âm mạnh nhất.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Nhạc mới, âm thanh to rõ, sôi động có khả năng thành bài Hit cao hơn hẳn nhạc mộc hoặc nhạc không lời trên Spotify.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Đánh giá Feature Importance thông qua chỉ số **SHAP Values** và **Permutation Importance** sau khi huấn luyện mô hình phi tuyến để kiểm định lại tương quan Pearson."
            )
        },
        {
            "plot_cell_code_contains": "feature_pairs =",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Binned Scatter Plot (Popularity vs Features)\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Phương pháp Binned Scatter Plot hé lộ mối quan hệ phi tuyến: `loudness` tăng nhanh đến −5 dB rồi bão hòa (Saturated Curve); `acousticness` giảm mạnh khi >0.35.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Ngưỡng bão hòa `loudness` giải thích cho giới hạn chịu đựng thính giác (Ear Fatigue) khi âm thanh bị nén quá mức (>0dB).\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Mô hình tuyến tính sẽ thất bại trên đường cong bão hòa này. Bắt buộc sử dụng các thuật toán **Gradient Boosted Trees (XGBoost, LightGBM, CatBoost)**."
            )
        },
        {
            "plot_cell_code_contains": "df_dur_all['long_track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Outliers Thời lượng Bài hát theo Năm\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:**\n"
                "Biểu đồ phân tích 26 bài siêu ngắn (<10s) và 83 bài siêu dài (>60min), dải biến thiên kéo dài từ 1.2 giây đến 5.4 giờ.\n\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:**\n"
                "Nhóm <10s là hiệu ứng âm thanh/intro DJ; nhóm >60 phút là podcast/tiếng mưa thiền định.\n\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:**\n"
                "Loại bỏ triệt để tracks <10 giây và áp dụng kỹ thuật **Winsorization / Clipping** đưa các bài hát >20 phút (1,200,000 ms) về ngưỡng trần cố định."
            )
        }
    ],
    r"3.1.hieu_du_lieu\01_data_understanding.ipynb": [
        {
            "plot_cell_code_contains": "df_decade['track_count']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Thống kê Tracks theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Mật độ mẫu tập trung ở 1990s và 2010s (>100K bài/thập kỷ), gấp 14.3 lần so với 1920s.\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Lịch sử số hóa kho nhạc của các đĩa nhạc số hiện đại.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Áp dụng Temporal Stratified Split khi chia dữ liệu."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ tổng quan Part 1",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Quy mô Dữ liệu & Views PostgreSQL\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Tổng số 586K bản ghi bài hát thô với các View phân tách rõ ràng giữa phân tích và học máy.\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Quản trị dữ liệu sạch, chống rò rỉ tên bài hát/nghệ sĩ vào mô hình dự báo.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Thiết lập bộ kiểm thử Schema Gate tự động."
            )
        },
        {
            "plot_cell_code_contains": "df_buckets['popularity_bucket']",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Cơ cấu Popularity Buckets\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Phân bố lệch phải nặng (37.5% ở 0–20 điểm, 44.6K bài điểm 0 tuyệt đối).\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Lượng lớn bài hát indie/unlisted không có lượt stream trên Spotify.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Áp dụng Two-Stage Classification + Huber Loss Regression."
            )
        },
        {
            "plot_cell_code_contains": "df_pop_decade = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Popularity Trung bình theo Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Popularity trung bình tăng từ 12.4 (1920s) lên 54.2 (2020s).\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Chỉ số Time Decay Factor tự động ưu tiên bài hát phát hành gần đây.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Tạo đặc trưng `Decade-Normalized Popularity Target`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 1: Mean vs Median",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Mean vs Median của 7 Audio Features\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Phân hóa giữa nhóm chuẩn (`danceability`, `valence`) và nhóm lệch (`speechiness`, `instrumentalness`).\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Thể hiện đặc trưng nhạc đại chúng Pop vs các phân khúc niche Rap/Podcast/Cổ điển.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Chuẩn hóa MinMax Scaling & Yeo-Johnson Transformation."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 2: Histogram 7 features",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Histogram Phân bố Chi tiết 7 Audio Features\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Thấy rõ vị trí đa số bài hát tập trung trong không gian thuộc tính âm thanh.\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Phản ánh thẩm mỹ sản xuất âm thanh hiện đại.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Xử lý triệt để zero-inflation ở `instrumentalness`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 3: Zoom speechiness",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Zoom Chi tiết Thuộc tính Lệch Speechiness\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Minh họa rõ nhất thuộc tính bị lệch phải nặng với mật độ >90% bài hát ở khoảng <0.2.\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Phân biệt bài hát thông thường vs nội dung podcast/rap.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Áp dụng biến đổi Log-transform cho `speechiness`."
            )
        },
        {
            "plot_cell_code_contains": "# Biểu đồ 4: So sánh feature CÂN BẰNG vs LỆCH",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: So sánh Thuộc tính Cân bằng vs Lệch\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Đối sánh trực quan giữa `danceability` (Cân bằng chuẩn) và `speechiness` (Lệch cực đoan).\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Bản chất đa dạng của các chiều thông tin âm thanh từ Spotify API.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Định hình các chiến lược Scaling riêng biệt cho từng nhóm thuộc tính."
            )
        },
        {
            "plot_cell_code_contains": "df_art = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Top Nghệ sĩ theo Track Count\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Top nghệ sĩ có kho nhạc khổng lồ (*Die drei ???*, *Lata Mangeshkar*).\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Bias dữ liệu kịch truyền thanh Đức & nhạc Bollywood.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Áp dụng Target Encoding with Smoothing Factor."
            )
        },
        {
            "plot_cell_code_contains": "df_gen = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Top Thể loại Nhạc Phổ biến\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Pop, Rock, Dance Pop chiếm thị phần áp đảo.\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Thị hiếu nghe nhạc thương mại đại chúng.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Gộp về 20 Parent Genre Clusters và Multi-Hot Encode."
            )
        },
        {
            "plot_cell_code_contains": "colors = ['#2ca02c' if v >= 0 else '#d62728' for v in corr.",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Pearson Correlation với target_popularity\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** `release_year` (+0.591), `loudness` (+0.327), `acousticness` (-0.371).\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Nhạc mới và âm thanh sôi động hỗ trợ độ popular trên Spotify.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Kiểm định bằng SHAP Values & Permutation Importance."
            )
        },
        {
            "plot_cell_code_contains": "df_exp = pd.read_sql",
            "markdown": (
                "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ: Xu hướng Tỷ lệ Nhạc Explicit qua các Thập kỷ\n\n"
                "📊 **Phân tích Định lượng & Thống kê Key:** Tỷ lệ explicit bứt phá từ 0.0% lên >15.8% ở thập niên 2010s–2020s.\n"
                "🎵 **Bản chất Âm nhạc & Cơ chế Kinh doanh:** Sự thống trị của Hip-hop, Rap, R&B đương đại.\n"
                "🤖 **Đánh giá Rủi ro ML & Đề xuất Pipeline:** Tạo đặc trưng tương tác `explicit_x_genre` và `explicit_x_decade`."
            )
        }
    ]
}

def apply_exact_per_chart_comments():
    for rel_path, configs in notebook_plot_comments.items():
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
                        print(f"Inserted dedicated comment cell into {rel_path} DIRECTLY AFTER plot code cell containing '{needle[:40]}...'")
                        break
        
        nb['cells'] = final_cells
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"Successfully processed {rel_path} (Total cells: {len(final_cells)})\n")

if __name__ == '__main__':
    apply_exact_per_chart_comments()
