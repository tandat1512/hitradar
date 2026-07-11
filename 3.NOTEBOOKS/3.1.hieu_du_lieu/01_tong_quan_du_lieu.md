# 01 — Tổng quan dữ liệu HitRadar

> Nguồn số liệu: `NB01 executed output`, `EDA_INSIGHTS_REPORT.md`

---

## Dataset này là gì?

HitRadar Pro dùng dữ liệu từ **Spotify** — một tập hợp thông tin về bài hát, nghệ sĩ, thể loại âm nhạc, và các chỉ số âm thanh do Spotify tự tính toán.

Mục tiêu cuối cùng: xây dựng model dự đoán **một bài hát có khả năng nổi tiếng (popular) không** dựa trên các đặc điểm âm thanh và metadata của nó.

---

## Số liệu tổng quan

| Chỉ số | Giá trị |
|--------|---------|
| Tổng số bài hát (tracks) | **586,672** |
| Nghệ sĩ có ít nhất 1 bài | **81,776** |
| Tổng genres trong hệ thống | **5,366** |
| Genres xuất hiện ở track-level | **4,672** |
| Năm phát hành sớm nhất | **1921** |
| Năm phát hành mới nhất | **2021** |
| Tổng số năm | **101 năm** |
| Tổng số thập kỷ | **12** (1920s → 2020s) |

---

## Tracks, Artists, Genres là gì — và khác nhau thế nào?

### Track (bài hát)
Một track là một bài hát cụ thể trên Spotify, có:
- Tên bài (`name`)
- Mã định danh duy nhất (`track_id`)
- Điểm phổ biến (`popularity`) — đây là **target/label** của model ML
- Các chỉ số âm thanh (danceability, energy, valence, ...)
- Ngày phát hành

Một track có thể có **nhiều nghệ sĩ** (ví dụ: bài hát song ca, hoặc feat.).

### Artist (nghệ sĩ)
Một artist là người hoặc nhóm tạo ra bài hát.  
Dataset có **1,162,095 artists** trong `clean.artists`, nhưng chỉ **81,776** trong số đó có ít nhất 1 bài hát nằm trong dataset tracks.

Một artist có thể có nhiều genres — Spotify gán genre cho **artist**, không gán trực tiếp cho track.

### Genre (thể loại)
Genre mô tả phong cách âm nhạc (rock, pop, jazz, classical, ...).  
Trong dataset:
- `clean.genres` có **5,366 genres** tổng cộng
- Nhưng chỉ **4,672 genres** xuất hiện trong phân tích track-level (vì 694 genres thuộc artists không có track trong dataset)

**Điểm quan trọng:** Genre được gán cho **artist**, không phải cho track. Vì vậy để biết bài hát thuộc genre nào, phải đi qua đường:  
`track → artist → genre`

---

## Dữ liệu này được tổ chức thế nào?

Ba tầng (layers):

```
RAW LAYER          ← dữ liệu gốc từ file CSV, chưa xử lý
     ↓
CLEAN LAYER        ← đã làm sạch, chuẩn hoá, kiểm tra chất lượng
     ↓
ANALYTICS LAYER    ← views tổng hợp, sẵn sàng để phân tích và ML
```

EDA notebooks chỉ đọc từ **analytics layer** — không chạm vào raw hay clean trực tiếp.

---

## Dataset này dùng để làm gì?

**Mục tiêu ngắn hạn (Feature 1.7):** Phân tích khám phá (EDA) — hiểu dữ liệu trước khi làm ML.

**Mục tiêu trung hạn (Feature 1.8):** Xuất ML-safe dataset — tập dữ liệu sạch, không có data leakage, sẵn sàng train.

**Mục tiêu dài hạn (EPIC 2):** Train model dự đoán popularity của bài hát dựa trên audio features và metadata.

---

## Những điều không nên hiểu sai

| Hiểu sai | Đúng là |
|----------|---------|
| Dataset có 586K bài hát phổ biến | Không — phần lớn (75%) có popularity dưới 40/100 |
| Popularity phản ánh chất lượng bài hát | Không — nó phản ánh số stream gần đây trên Spotify |
| Genre gắn trực tiếp vào track | Không — genre gắn vào artist, sau đó mới suy ra cho track |
| 5,366 genres đều có track | Không — 694 genres không có track nào trong dataset |
| Dataset đại diện đều cho mọi thập kỷ | Không — lệch nặng về 1990s (108K) và 2010s (105K) |
