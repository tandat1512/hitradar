# 04 — Giải thích Track, Artist, Genre

> Nguồn: `ANALYTICS_VIEWS_REPORT.md`, `EDA_INSIGHTS_REPORT.md`, `NB05 executed output`

---

## Track là gì?

Một **track** = một bài hát cụ thể trên Spotify.

- Định danh: `track_id` (chuỗi ký tự, ví dụ `2lyaLEbGPn7i1paCfnuFZz`)
- Có tên (`name`), ngày phát hành, điểm popularity, 7+ audio features
- Dataset có **586,672 tracks**

Một track có thể có **nhiều artists** (song ca, feat., remix).

---

## Artist là gì?

Một **artist** = người hoặc nhóm tạo ra bài hát.

- Dataset có **1,162,095 artists** trong `clean.artists`
- Chỉ **81,776** có ít nhất 1 track trong dataset tracks
- Phần lớn artists có rất ít bài — phân bố **long-tail**

Ví dụ từ NB05: "Die drei ???" có 3,856 tracks nhưng đây là series audio drama Đức — mỗi tập = 1 track.

---

## Genre là gì?

Một **genre** = thể loại âm nhạc (rock, pop, jazz, classical, filmi, ...).

- `clean.genres` có **5,366 genres** tổng
- Chỉ **4,672 genres** xuất hiện trong track-level analysis (`vw_genre_trends`)
- Chênh lệch **694 genres** — thuộc artists không có track trong dataset (do coverage gap 96.54%)

---

## Vì sao genre lấy từ artist, không trực tiếp từ track?

Spotify **không gán genre trực tiếp cho track**. Genre được gán cho **artist**.

Để biết bài hát thuộc genre nào, phải đi theo chuỗi:

```
track  →  track_artists  →  artist  →  artist_genres  →  genre
```

Ví dụ: Bài "Shape of You" → artist Ed Sheeran → genres: pop, uk pop, singer-songwriter.

**Hệ quả:** Một bài hát có thể mang **nhiều genres** nếu có nhiều artists, hoặc nếu artist đó có nhiều genres.

---

## Vì sao clean.genres = 5,366 nhưng track-linked = 4,672?

| Số | Ý nghĩa |
|----|---------|
| 5,366 | Tổng genres trong hệ thống (`clean.genres`) |
| 5,366 | Genres có trong `clean.artist_genres` (mọi genre đều có artist) |
| 4,672 | Genres xuất hiện khi join đến track-level (`vw_genre_trends`) |
| 694 | Chênh lệch — genres thuộc artists bị skip trong 3.46% coverage gap |

694 genres này không phải lỗi data — là hệ quả của `track_artists_coverage = 96.54%` (26,224 cặp track-artist bị skip).

*Nguồn: `EDA_INSIGHTS_REPORT.md`, query xác minh trong hotfix Feature 1.7.*

---

## Vì sao một track có thể có nhiều genres?

Ba nguyên nhân chồng nhau:

1. **Nhiều artists:** Bài song ca 2 nghệ sĩ → mỗi artist có genres riêng
2. **Artist có nhiều genres:** Ed Sheeran có cả "pop" lẫn "uk pop"
3. **Cùng genre lặp lại:** 2 artists cùng genre "rock" → nếu không dedup sẽ đếm 2 lần

---

## Vì sao phải dùng DISTINCT trong `vw_genre_trends`?

**Vấn đề duplicate-weighting:**

Giả sử bài "ABC" có 3 artists, cả 3 đều có genre "pop":
- Không DISTINCT → đếm bài "ABC" vào "pop" **3 lần**
- Có DISTINCT → đếm **1 lần**

`vw_genre_trends` dùng CTE:

```sql
SELECT DISTINCT (track_id, genre_id, decade, ...)
```

Sau đó `COUNT(DISTINCT track_id)` để đảm bảo mỗi track chỉ đóng góp 1 lần cho mỗi genre-decade pair.

*Nguồn: `ANALYTICS_VIEWS_REPORT.md` section vw_genre_trends.*

---

## Vì sao không nên one-hot toàn bộ 4,672 genres trong ML?

| Vấn đề | Giải thích |
|--------|-----------|
| **Sparse** | Hầu hết genres có rất ít tracks — one-hot tạo 4,672 cột, phần lớn = 0 |
| **Memory** | 586,672 × 4,672 = ma trận cực lớn, không thực tế |
| **Overfitting** | Model học noise từ genres hiếm thay vì pattern thật |
| **Bias** | Top genres (rock, adult standards) chiếm ưu thế — one-hot không cân bằng được |

**Thay thế đề xuất (EPIC 2):**
- Top-N genres (ví dụ top 50) + category "other"
- Genre embedding
- Không dùng genre nếu chưa có chiến lược rõ

*Nguồn: `FEATURE_1_7_COMPLETION_REPORT.md` ML Handoff Notes.*

---

## Tóm tắt quan hệ

```
┌─────────┐     track_artists     ┌─────────┐     artist_genres     ┌─────────┐
│  TRACK  │ ──────────────────── │  ARTIST │ ──────────────────── │  GENRE  │
│ 586,672 │   (730,946 pairs)    │1,162,095│   (468,680 pairs)    │  5,366  │
└─────────┘   coverage 96.54%    └─────────┘                      └─────────┘
                                                                      │
                                                              track-linked: 4,672
```

**Nhớ:** Genre không gắn trực tiếp vào track. Mọi phân tích genre đều phải đi qua artist.
