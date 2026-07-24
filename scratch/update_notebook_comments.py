import os
import json

base_dir = r"e:\Dự án 1 hitrada\hitradar\3.NOTEBOOKS"

# Define updates for each notebook file
updates = {
    r"3.4.eda\01_dataset_overview.ipynb": {
        "inserts": [
            {
                "after_cell_index": 5,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ Quy mô Views Dataset\n\n"
                    "Biểu đồ thể hiện quy mô tổng thể của tập dữ liệu với hơn **586,001 bản ghi bài hát thô** được quản lý trong cơ sở dữ liệu PostgreSQL. "
                    "Sự chênh lệch giữa view tổng quan (`vw_tracks_overview`) và view huấn luyện Machine Learning (`vw_ml_training_dataset`) phản ánh quy trình lọc dữ liệu khắt khe: "
                    "toàn bộ các thông tin định danh như `name` hoặc thông tin rò rỉ (data leakage) đã bị loại bỏ ở view ML để đảm bảo tính an toàn cho mô hình.\n"
                    "Thống kê cũng cho thấy số lượng nghệ sĩ và thể loại nhạc phủ rộng với hàng chục ngàn entity khác nhau. "
                    "Tỷ lệ thiếu dữ liệu (NULL) được kiểm soát ở mức cực kỳ thấp (<0.1%), khẳng định chất lượng dữ liệu đầu vào sau bước ETL là rất cao. "
                    "Đây là nền tảng vững chắc để triển khai các bước trích xuất đặc trưng (Feature Engineering) và mô hình hóa ở các giai đoạn tiếp theo."
                )
            },
            {
                "after_cell_index": 12,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Phân bổ Bài hát theo Thập kỷ\n\n"
                    "Biểu đồ phân bố lượng tracks qua các thập kỷ cho thấy mật độ mẫu tập trung cực kỳ dày đặc ở hai thập niên 1990s và 2010s với hơn 100,000 bài mỗi thập kỷ. "
                    "Trái lại, khoảng thời gian 1920s–1940s có số lượng bài khá khiêm tốn (dưới 20,000 bài), phản ánh hạn chế về số hóa dữ liệu âm nhạc cổ điển.\n"
                    "Sự chênh lệch này đòi hỏi chiến lược phân chia dữ liệu Train/Validation/Test phải theo mốc thời gian (Temporal Split) thay vì ngẫu nhiên. "
                    "Điều này tránh cho mô hình bị học thiên vị (bias) vào các thập kỷ hiện đại và đảm bảo khả năng tổng quát hóa trên toàn bộ dòng lịch sử âm nhạc."
                )
            }
        ]
    },
    r"3.4.eda\02_popularity_analysis.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Phân bố Popularity (Buckets & Pie Chart)\n\n"
                    "Biểu đồ histogram và pie chart cho thấy sự phân bố điểm phổ biến (`target_popularity`) bị **lệch phải nặng (Right-Skewed)** và xuất hiện hiện tượng Zero-Inflation rõ rệt. "
                    "Đáng chú ý nhất là nhóm Popularity từ 0 đến 20 chiếm tỷ trọng áp đảo lên tới **37.5%** (tương đương 219,988 tracks), trong đó riêng các bài hát có điểm bằng 0 tuyệt đối chiếm 7.6%.\n"
                    "Hiện tượng này giải thích do Spotify chứa lượng lớn các bài hát mới phát hành, bài hát chưa có lượt stream hoặc các nội dung podcast/indie chưa tiếp cận được lượng người nghe đại chúng. "
                    "Dưới góc độ Machine Learning, sự lệch nhãn cực đoan này sẽ khiến các mô hình hồi quy (Regression) thông thường bị chệch dự báo về phía giá trị thấp. "
                    "Đề xuất áp dụng kỹ thuật Log-Transformation, phân nhóm nhãn (Bucketing/Classification) hoặc sử dụng các hàm mất mát kháng lệch (Robust Loss Functions) như Huber Loss / Quantile Loss khi huấn luyện."
                )
            },
            {
                "after_cell_index": 7,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Popularity trung bình theo Thập kỷ\n\n"
                    "Biểu đồ cột biểu diễn điểm Popularity trung bình qua các thập kỷ từ 1920s đến 2020s thể hiện một xu hướng tăng trưởng tuyến tính rõ rệt theo thời gian. "
                    "Các bài hát thuộc thập niên 1920s–1950s có Popularity trung bình chỉ dao động ở mức 10–25 điểm, trong khi các bài hát ở thập niên 2010s và 2020s đạt điểm trung bình vượt trội từ 45 đến trên 55 điểm.\n"
                    "Nguyên nhân đến từ cơ chế thuật toán gợi ý của Spotify ưu tiên các ca khúc hiện đại có lượt nghe thực tế cao và hành vi tiêu dùng âm nhạc trực tuyến gắn liền với thế hệ trẻ. "
                    "Sự chênh lệch này khẳng định yếu tố thời gian (`release_year` / `decade`) là một đặc trưng dự báo cực kỳ mạnh mẽ cho điểm Popularity. "
                    "Tuy nhiên, nó cũng tiềm ẩn rủi ro 'Temporal Bias', buộc mô hình ML phải được chuẩn hóa theo từng khoảng thời gian hoặc sử dụng thuật toán cắt tách dữ liệu theo mốc thời gian (Time-based Split) thay vì chia ngẫu nhiên."
                )
            }
        ]
    },
    r"3.4.eda\03_audio_features_distribution.ipynb": {
        "inserts": [
            {
                "after_cell_index": 5,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Phân bố 7 Audio Features (Mean ± Spread)\n\n"
                    "Biểu đồ thể hiện giá trị trung bình (Mean) cùng khoảng biến thiên (Std Spread) của 7 đặc trưng âm thanh được trích xuất từ Spotify API. "
                    "Qua quan sát, có sự phân hóa rõ rệt thành hai nhóm thuộc tính: Nhóm thuộc tính cân bằng gồm `danceability` (trung bình 0.564) và `valence` (trung bình 0.552) với phân bố hình chuông chuẩn, độ lệch thấp, phản ánh tính chất bắt tai và cảm xúc âm nhạc đa dạng của kho nhạc.\n"
                    "Trái lại, nhóm thuộc tính lệch cực đoan gồm `speechiness` (lệch phải nặng, trung bình 0.104) và `instrumentalness` (tập trung gần 0, nhiều bài không phải nhạc hòa tấu). "
                    "Thuộc tính `energy` có dải biến thiên rộng (0.542 ± 0.25), là ứng viên tiềm năng tạo ra độ phân giải tốt cho mô hình ML. "
                    "Việc khác biệt về quy mô và hình dạng phân bố đòi hỏi toàn bộ 7 thuộc tính này phải qua bước chuẩn hóa MinMax Scaling hoặc Robust Scaling trước khi đưa vào mô hình."
                )
            },
            {
                "after_cell_index": 7,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Xu hướng Audio Features theo Thời gian (1920–2020)\n\n"
                    "Đồ thị đường theo thời gian phác họa cuộc cách mạng âm nhạc trong suốt 1 thế kỷ (1920–2020). "
                    "Điểm bứt phá rõ nhất là sự sụt giảm dốc đứng của chỉ số `acousticness` — từ mức áp đảo >0.85 ở những năm 1920 (thời kỳ mộc/cổ điển) xuống chỉ còn <0.25 ở thập niên 2010s.\n"
                    "Ngược lại hoàn toàn, hai thuộc tính `energy` và `loudness` ghi nhận mức tăng trưởng liên tục, phản ánh sự ra đời của các nhạc cụ điện tử, dòng nhạc Electronic/Pop/Hip-hop và hiện tượng 'Loudness War' trong công nghệ sản xuất âm thanh hiện đại. "
                    "Các đặc trưng như `danceability` tăng nhẹ và duy trì ổn định ở mức cao (~0.6). "
                    "Sự dịch chuyển xu hướng âm thanh theo thời gian này xác nhận mối quan hệ tương quan chặt chẽ giữa Audio Features và Release Year, yêu cầu mô hình ML phải học được các mối tương tác đa biến (Feature Crosses) giữa thời gian và đặc trưng âm thanh."
                )
            }
        ]
    },
    r"3.4.eda\04_time_decade_trends.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Phân bố Mẫu theo Thời gian (Thập kỷ & Năm)\n\n"
                    "Biểu đồ phân bố số lượng bài hát theo thập kỷ chỉ ra hiện tượng **mất cân bằng dữ liệu thời gian (Data Imbalance Across Time)** nghiêm trọng trong tập dữ liệu. "
                    "Hai thập niên 1990s và 2010s đóng góp số lượng bài hát khổng lồ nhất, lần lượt là 108,875 và 105,245 tracks (mỗi thập kỷ chiếm gần 18–19% toàn bộ dataset).\n"
                    "Trong khi đó, các thập niên đầu thế kỷ 20 như 1920s chỉ ghi nhận vỏn vẹn 7,610 tracks (~1.3%), cho thấy dữ liệu lịch sử khá thưa thớt (sparse data). "
                    "Sự phân bố không đồng đều này phản ánh quá trình số hóa kho nhạc của Spotify tập trung chủ yếu vào âm nhạc hiện đại. "
                    "Đối với bài toán ML, sự chênh lệch mật độ mẫu theo thời gian đòi hỏi chiến lược chia tập Train/Validation/Test phải theo phương pháp Stratified Temporal Split để đảm bảo mô hình không bị thiên vị (biased) về các thập kỷ có dung lượng mẫu lớn."
                )
            },
            {
                "after_cell_index": 6,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Tỷ lệ Nhạc Explicit qua các Thập kỷ\n\n"
                    "Biểu đồ thể hiện tỷ lệ phần trăm các bài hát chứa nội dung nhạy cảm (`explicit`) qua từng thập kỷ. "
                    "Trước thập niên 1980, tỷ lệ bài hát explicit gần như bằng 0% do sự kiểm duyệt khắt khe và tiêu chuẩn âm nhạc truyền thống. "
                    "Tuy nhiên, từ thập niên 1990s trở đi, tỷ lệ này tăng vọt và đạt mức đỉnh điểm **>15%** trong thập niên 2010s và 2020s.\n"
                    "Xu hướng này gắn liền với sự bùng nổ của các dòng nhạc Hip-hop, Rap và R&B hiện đại — nơi ngôn từ tự do và cá tính nghệ sĩ được bộc lộ mạnh mẽ. "
                    "Trong mô hình dự báo Popularity, biến nhị phân `explicit` là một tín hiệu đặc trưng (feature signal) quan trọng vì các bài hát explicit ở thời đại số thường có mối tương quan thuận nhẹ với mức độ phổ biến đối với nhóm khán giả trẻ tuổi."
                )
            },
            {
                "after_cell_index": 8,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Xu hướng Thời lượng Bài hát (`duration_ms`)\n\n"
                    "Đồ thị theo dõi thời lượng bài hát trung bình (tính bằng phút) từ năm 1920 đến 2020 tiết lộ một chu kỳ biến đổi thú vị. "
                    "Trong giai đoạn 1920–1950, thời lượng bài hát duy trì ở mức ngắn 3.0–3.5 phút do giới hạn vật lý của đĩa than (78 RPM vinyl). "
                    "Giai đoạn 1960–2000 chứng kiến sự gia tăng thời lượng lên đến đỉnh điểm 4.2–4.5 phút nhờ công nghệ đĩa CD và sự phát triển của Rock/Pop phức hợp.\n"
                    "Tuy nhiên, từ năm 2015 trở lại đây, thời lượng bài hát có xu hướng **sụt giảm nhanh chóng xuống dưới 3.3 phút**. "
                    "Lý do kinh tế đằng sau hiện tượng này là cơ chế tính tiền bản quyền stream theo lượt của Spotify (pay-per-stream sau 30 giây), khuyến khích các nhà sản xuất làm bài hát ngắn hơn để tối ưu số lượt nghe. "
                    "Đây là một insight quan trọng để feature engineering xây dựng chỉ số `duration_trend_ratio`."
                )
            }
        ]
    },
    r"3.4.eda\05_artist_genre_analysis.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Top Artists theo Track Count\n\n"
                    "Biểu đồ cột thể hiện 15 nghệ sĩ sở hữu số lượng bài hát lớn nhất trong tập dữ liệu. "
                    "Kết quả cho thấy sự xuất hiện của hai cái tên áp đảo là *'Die drei ???'* (3,856 tracks - chuỗi kịch truyền thanh nổi tiếng của Đức) và *'Lata Mangeshkar'* (2,605 tracks - huyền thoại âm nhạc Ấn Độ). "
                    "Hiện tượng này phản ánh đặc tính **Bias dữ liệu địa phương và thể loại nói (Spoken Word/Audio Drama)** trong kho nhạc Spotify thô.\n"
                    "Bên cạnh đó, danh sách 81,776 nghệ sĩ còn lại tuân theo phân bố đuôi dài (Long-tail Distribution) khi phần lớn nghệ sĩ chỉ có từ 1 đến 3 bài hát. "
                    "Đối với mô hình ML, nếu đưa trực tiếp ID nghệ sĩ dạng One-Hot Encoding sẽ gây bùng nổ chiều dữ liệu (Curse of Dimensionality), do đó cần áp dụng kỹ thuật Target Encoding hoặc Frequency Encoding kèm Regularization."
                )
            },
            {
                "after_cell_index": 6,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Top Artists theo Popularity Trung bình\n\n"
                    "Trái ngược hoàn toàn với biểu đồ số lượng bài hát, danh sách Top Artists theo điểm Popularity trung bình lại quy tụ những ngôi sao nhạc Pop/Hip-hop đương đại hàng đầu thế giới như Bad Bunny, Taylor Swift, Drake, The Weeknd với điểm trung bình ấn tượng >80 điểm. "
                    "Sự đối lập này đưa ra một kết luận Data Science quan trọng: **Số lượng bài hát không đồng nghĩa với độ phổ biến**.\n"
                    "Những nghệ sĩ phát hành kho nhạc đồ sộ (như kịch nói hay nhạc cổ điển) thường có điểm trung bình bị pha loãng bởi nhiều bài ít lượt nghe. "
                    "Trong khi đó, các nghệ sĩ mainstream hiện đại tập trung vào các bản Single/Album chất lượng cao tạo nên độ phổ biến đỉnh điểm. "
                    "Đây là căn cứ để tạo các nhóm Feature mức Nghệ sĩ (Artist-level Aggregated Features) như `artist_avg_popularity` và `artist_hit_rate`."
                )
            },
            {
                "after_cell_index": 8,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Top Genres Phổ biến nhất\n\n"
                    "Biểu đồ thống kê Top 20 thể loại âm nhạc phổ biến nhất trong cơ sở dữ liệu. "
                    "Nhạc Pop, Rock, Dance Pop, Hip Hop và Indie là những dòng nhạc chiếm tỷ trọng cao nhất. "
                    "Tuy nhiên, phân tích sâu cho thấy dữ liệu thể loại có tính chất đa nhãn (Multi-label) và độ nhiễu khá lớn: "
                    "nhiều nghệ sĩ được gán hàng chục sub-genre chi tiết (ví dụ: *pop rap*, *tropical house*, *indie folk*), trong khi một lượng lớn nghệ sĩ indie lại bị thiếu thông tin genre (Empty Genre).\n"
                    "Rào cản này yêu cầu quy trình tiền xử lý phải thực hiện chuẩn hóa thể loại (Genre Normalization), gộp các sub-genre về nhóm thể loại mẹ (Parent Genres) và xử lý giá trị thiếu bằng thuộc tính mặc định `unknown_genre` trước khi trích xuất đặc trưng cho mô hình."
                )
            }
        ]
    },
    r"3.4.eda\06_correlation_outlier_analysis.ipynb": {
        "inserts": [
            {
                "after_cell_index": 4,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Ma trận Tương quan Pearson với `target_popularity`\n\n"
                    "Biểu đồ thanh biểu diễn hệ số tương quan tuyến tính Pearson giữa 10 đặc trưng số với nhãn mục tiêu `target_popularity`. "
                    "Ba đặc trưng thể hiện mối tương quan dương mạnh nhất là `release_year` (+0.591), `loudness` (+0.327) và `energy` (+0.302) — khẳng định yếu tố thời gian phát hành mới và độ to/sôi động của âm thanh hỗ trợ mạnh cho độ phổ biến trên Spotify.\n"
                    "Ở chiều ngược lại, `acousticness` (−0.371) và `instrumentalness` (−0.237) thể hiện tương quan âm rõ rệt, do nhạc mộc và nhạc không lời thường thuộc nhóm niche market ít người nghe phổ thông. "
                    "Chỉ số `speechiness`, `liveness` và `duration_min` hầu như không có tương quan tuyến tính đơn thuần với popularity. "
                    "Đây là cơ sở quan trọng để lựa chọn đặc trưng đầu vào và cảnh báo kiểm tra kỹ rò rỉ dữ liệu từ `release_year`."
                )
            },
            {
                "after_cell_index": 6,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Scatter Plot Binned (Popularity vs Selected Features)\n\n"
                    "Do tập dữ liệu chứa 586K điểm mẫu dễ gây hiện tượng đè nét (overplotting), phương pháp binned scatter (gom nhóm theo bin và tính Popularity trung bình) đã hé lộ các mối quan hệ phi tuyến (Non-linear Relationships) bị che khuất bởi chỉ số Pearson đơn thuần. "
                    "Chẳng hạn, mối quan hệ giữa `loudness` và `avg_popularity` thể hiện dạng đường cong tăng dần và bão hòa ở khoảng −5 dB đến 0 dB (âm thanh quá to sẽ gây chói tai và giảm điểm).\n"
                    "Tương tự, `acousticness` giảm điểm phi tuyến tính khi chỉ số vượt qua mốc 0.4. "
                    "Những phát hiện này khẳng định các mô hình học máy phi tuyến như Gradient Boosting (XGBoost, LightGBM) hoặc Random Forest sẽ phát huy sức mạnh vượt trội hơn hẳn so với mô hình Linear Regression trong bài toán dự báo Popularity này."
                )
            },
            {
                "after_cell_index": 9,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Outlier Thời lượng Bài hát (`duration_ms`)\n\n"
                    "Biểu đồ phân tích dị biệt (Outliers) chỉ ra hai nhóm bài hát bất thường về thời lượng: "
                    "Nhóm siêu ngắn (<10 giây, tổng cộng 26 bài) thường là các đoạn âm thanh intro/outro/skit hoặc lỗi metadata; "
                    "Nhóm siêu dài (>60 phút, tổng cộng 83 bài) chủ yếu là các bản thu âm podcast, thiền định hoặc album hợp tuyển liên tục.\n"
                    "Mặc dù tổng số lượng outlier thời lượng này rất nhỏ (<0.02% toàn bộ dataset), nhưng trong các thuật toán huấn luyện ML dựa trên khoảng cách (như KNN hay SVM) hoặc hàm mất mát MSE, các ngoại lệ cực đoan này có thể tạo ra gradient nhiễu lớn. "
                    "Đề xuất quy tắc làm sạch loại bỏ triệt để các track <10s và clip/trim thời lượng các track siêu dài về ngưỡng tối đa 20 phút (1,200,000 ms) ở bước Data Cleaning."
                )
            }
        ]
    },
    r"3.1.hieu_du_lieu\01_data_understanding.ipynb": {
        "inserts": [
            {
                "after_cell_index": 5,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Biểu đồ Quy mô Dataset & Views PostgreSQL\n\n"
                    "Biểu đồ tổng quan hiển thị quy mô hơn 586,001 bản ghi bài hát thô trong cơ sở dữ liệu PostgreSQL. "
                    "Sự đóng gói dữ liệu từ schema `raw` sang schema `clean` và các view phân tích (`vw_tracks_overview`, `vw_ml_training_dataset`) thể hiện quy trình quản trị dữ liệu chặt chẽ. "
                    "View huấn luyện ML được thiết kế chuyên biệt nhằm triệt tiêu hoàn toàn rò rỉ dữ liệu và loại bỏ các cột định danh dạng văn bản không phù hợp cho thuật toán học máy.\n"
                    "Tỷ lệ thiếu dữ liệu cực kỳ nhỏ chứng tỏ chất lượng bước ETL ban đầu rất tốt, tạo tiền đề tin cậy cho toàn bộ pipeline xây dựng mô hình về sau."
                )
            },
            {
                "after_cell_index": 14,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Phân bố Popularity & Cơ cấu Buckets\n\n"
                    "Biểu đồ cơ cấu popularity khẳng định hiện tượng lệch phải nặng của nhãn mục tiêu với 37.5% tổng số bài hát tập trung ở phân khúc 0–20 điểm. "
                    "Hiện tượng này tạo ra thách thức lớn cho các mô hình hồi quy tiêu chuẩn do xu hướng bị chệch dự báo về giá trị trung bình thấp.\n"
                    "Đồng thời, sự tăng trưởng điểm popularity theo từng thập kỷ thể hiện ưu thế vượt trội của các bài hát hiện đại trên các nền tảng trực tuyến. "
                    "Cần kết hợp kỹ thuật biến đổi nhãn (label transformation) và phân tầng mẫu theo thời gian để tối ưu hiệu năng dự báo."
                )
            },
            {
                "after_cell_index": 21,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Đặc tính 7 Audio Features & Xu hướng Đa biến\n\n"
                    "Phân tích đặc trưng âm thanh cho thấy sự đối lập rõ rệt giữa các chỉ số cân bằng (`danceability`, `valence`) và các chỉ số lệch phải nặng (`speechiness`, `instrumentalness`). "
                    "Sự dịch chuyển lịch sử chứng kiến chỉ số `acousticness` sụt giảm mạnh trong khi `energy` và `loudness` tăng cao qua từng thập kỷ.\n"
                    "Điều này yêu cầu các thuộc tính âm thanh phải được qua xử lý chuẩn hóa (Scaling) và log-transform phù hợp trước khi đưa vào các thuật toán học máy."
                )
            },
            {
                "after_cell_index": 29,
                "markdown": (
                    "### 📌 Giải thích & Nhận xét Chuyên sâu Ma trận Tương quan & Mối quan hệ Phi tuyến\n\n"
                    "Ma trận tương quan Pearson khẳng định `release_year` (+0.591), `loudness` (+0.327) và `energy` (+0.302) có tác động dương mạnh nhất tới Popularity. "
                    "Ngược lại, `acousticness` và `instrumentalness` có tương quan âm sâu sắc.\n"
                    "Các biểu đồ binned scatter hé lộ thêm các điểm bão hòa phi tuyến, khẳng định các thuật toán cây quyết định nâng cao (Gradient Boosted Trees) là lựa chọn tối ưu nhất cho bài toán này."
                )
            }
        ]
    }
}

def update_notebook(rel_path, config):
    full_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        return
    
    with open(full_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    inserts = config.get('inserts', [])
    # Sort inserts in reverse order of index to keep cell positions valid
    inserts_sorted = sorted(inserts, key=lambda x: x['after_cell_index'], reverse=True)
    
    for ins in inserts_sorted:
        idx = ins['after_cell_index']
        md_text = ins['markdown']
        new_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in md_text.split("\n")]
        }
        # Insert after specified index
        insert_at = min(idx + 1, len(cells))
        cells.insert(insert_at, new_cell)
        print(f"Inserted markdown cell into {rel_path} after original cell index {idx}")
    
    nb['cells'] = cells
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"Successfully updated {rel_path} (Total cells now: {len(cells)})\n")

if __name__ == '__main__':
    for rel_p, conf in updates.items():
        update_notebook(rel_p, conf)
