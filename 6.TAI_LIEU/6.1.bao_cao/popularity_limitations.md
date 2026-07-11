# POPULARITY LIMITATIONS

**Feature:** 1.8 — ML-Safe Dataset Handoff  
**Label:** `target_popularity` (Spotify popularity 0–100)  
**Owner:** Đạt  
**Nguồn:** EDA_INSIGHTS_REPORT.md, Feature 1.7 carry-forward

---

## 1. Popularity ≠ Chất lượng âm nhạc

Spotify **popularity** không đo chất lượng nghệ thuật. Đây là chỉ số **nhu cầu/nghe gần đây** trên nền tảng, phụ thuộc nhiều yếu tố ngoài âm nhạc học.

---

## 2. Yếu tố ảnh hưởng popularity

| Yếu tố | Ảnh hưởng |
|--------|-----------|
| Streams gần đây | Popularity phụ thuộc nhiều vào streams/activity gần đây trên nền tảng |
| Thời gian phát hành | Tracks mới có lợi thế hơn tracks cũ (time bias) |
| Nền tảng & thuật toán | Chỉ phản ánh Spotify, không phải toàn thị trường |
| Thị hiếu & xu hướng | Genre/decade trends thay đổi theo thời gian |
| Playlist exposure | Được đưa vào playlist lớn → popularity tăng nhanh |
| Marketing / artist fame | Không nằm trong baseline audio features |

---

## 3. Class / Distribution Imbalance

**Khoảng 75% tracks có popularity ≤ 40** (Feature 1.7 carry-forward).

### Bucket Distribution (586,672 tracks)

| Bucket | Count | % approx |
|--------|-------|----------|
| 0–20 | 219,988 | 37.5% |
| 21–40 | 219,003 | 37.3% |
| 41–60 | 122,813 | 20.9% |
| 61–80 | 24,132 | 4.1% |
| 81–100 | 736 | 0.1% |

### Zero Popularity

- **target_popularity = 0:** 44,690 tracks (~7.6%)
- Có thể là tracks ít stream, mới release, hoặc chưa được index đầy đủ — cần phân tích riêng ở EPIC 2.

---

## 4. Hệ quả cho ML (EPIC 2)

### Classification

- Phân phối lệch mạnh — cần xử lý class imbalance (weighting, stratified sampling, focal loss, v.v.).
- Bucket 81–100 chỉ 736 tracks — rất khó học tail class.

### Regression

- Đánh giá MAE/RMSE **và** phân tích error theo decade / popularity bucket.
- Metric trung bình có thể bị chi phối bởi mass ở bucket 0–40.
- Cân nhắc weighted metrics hoặc segment evaluation.

---

## 5. Giới hạn khi diễn giải model

- **Không nên** tuyên bố model dự đoán "hit song" tuyệt đối nếu chỉ dựa vào popularity.
- Popularity là proxy **thành công trên Spotify tại thời điểm snapshot**, không phải hit vĩnh viễn.
- `release_year` correlation +0.5909 — model có thể học "bài mới = popular hơn" thay vì audio quality.

---

## 6. Khuyến nghị báo cáo EPIC 2

1. Luôn nêu popularity limitations trong model card / report.
2. Báo cáo performance theo bucket và decade.
3. So sánh temporal vs random split để đo time bias.
4. Tránh overclaim: "predict hit" → nên là "estimate Spotify popularity proxy".

---

*Feature 1.8 — ML-Safe Dataset Handoff | HitRadar Pro*
