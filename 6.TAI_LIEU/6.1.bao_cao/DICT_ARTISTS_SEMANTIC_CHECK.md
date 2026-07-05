# DICT_ARTISTS SEMANTIC CHECK — TASK 1.2.0

> **Mục đích:** Xác minh `dict_artists.json` là nguồn genre hay related artist graph trước khi thiết kế genre pipeline.
> **Người thực hiện:** Đạt | **Ngày:** 2026-07-05 | **Script:** `9.SCRIPTS/verify_dict_artists_semantic.py`

---

## 1. Purpose

Task 1.2.0 yêu cầu xác minh semantic meaning của `dict_artists.json` trước khi thiết kế database schema,
đặc biệt là quyết định có dùng file này làm nguồn genre hay không.

---

## 2. Inputs

| Input | File | Size |
|-------|------|------|
| Artist IDs reference | `1.DỮ_LIỆU/1.1.raw/artists.csv` | 61.89 MB |
| Target file | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | 317.17 MB |

---

## 3. Method

1. Đọc toàn bộ `artists.csv.id` → set artist IDs tham chiếu.
2. Đọc `dict_artists.json`, lấy 20 sample key-value không rỗng.
3. Scan 50,005 values đầu tiên (từ các non-empty entries).
4. Tính overlap giữa values và `artists.csv.id`.
5. Kiểm tra pattern 22-char alphanumeric (Spotify Artist ID format).
6. Kết luận dựa trên overlap ratio và pattern ratio.

---

## 4. Results

| Chỉ số | Giá trị |
|--------|---------|
| `artists.csv` unique IDs | 1,162,095 |
| `dict_artists.json` keys | 573,856 |
| Values scanned (sample) | 50,005 |
| Matched to `artists.csv.id` | 50,005 |
| **Overlap ratio** | **100.00%** |
| 22-char pattern match | 50,005 / 50,005 = 100.00% |

### Sample key-values (10 non-empty entries)

| Key (artist_id) | Values (preview, max 5) | Value count |
|----------------|------------------------|-------------|
| `0DvvojCMIqsOT1Btiwvq1h` | `['3Y9UedETQztUmRuB2pYaGR', '6ng2L9Pwj7NeXm0vJW8LLr', '0QAlsftQZIVyNXDtK7PEt2', '32qUUy6h1wKd5jN4vRSF20', '7kc7HZFnOwUWd8dL8jypPf']` | 20 |
| `6S3nAGEmdt4nhPrtBJ56Ga` | `['5Tbx1DjctXEQnR9UBJmU9r', '6Dxf1ZaJBrpbumiqTTnlIH', '05GsKvp0yKuCyWQMsPAAmB', '0ipBu57ONv2AW0Pxpc2etO', '2N3LtIOsdqHwsSlVFVFxqd']` | 20 |
| `0VLMVnVbJyJ4oyZs2L3Yl2` | `['6yJIuZFLnlAe47DKobH45J', '5QNqh0mFcqoGsdzHGMvT1u', '3HDrX2OtSuXLW5dLR85uN3', '0Ik0N7B22ry8BvdxvDGnG0', '4tkGMeZkhOXyk4U9RzvP14']` | 20 |
| `0dt23bs4w8zx154C5xdVyl` | `['6yJIuZFLnlAe47DKobH45J', '0Ik0N7B22ry8BvdxvDGnG0', '7mCB2ez7kzv32Yuds8ltlL', '5YpG4yABnjezWZ4ugXZoMP', '3HDrX2OtSuXLW5dLR85uN3']` | 20 |
| `0pGhoB99qpEJEsBQxgaskQ` | `['5YpG4yABnjezWZ4ugXZoMP', '5qr3WvyioJJApp99FFfqob', '0zMJmvs0RriumGJSAiduOw', '0Ik0N7B22ry8BvdxvDGnG0', '4sBmoMtQBJXQMIxYwuLR5I']` | 20 |
| `3HDrX2OtSuXLW5dLR85uN3` | `['6yJIuZFLnlAe47DKobH45J', '5QNqh0mFcqoGsdzHGMvT1u', '0Ik0N7B22ry8BvdxvDGnG0', '0VLMVnVbJyJ4oyZs2L3Yl2', '0muEwnW8BH3RXdGnQyxEyo']` | 20 |
| `22mLrN5fkppmuUPsHx6i2G` | `['3NhV0B71sAoZu1FGHG4bK4', '04jItOTRWnT2GWXLjCEWjP', '52rqtO4q5VcEEnvxP9wvrr', '3nt4PBXVgQyj0KQHeE7tR4', '23OtctXQsEX9vMDXWsbkOH']` | 20 |
| `1OCPhFtvkZDLUJJkrJfD2G` | `['1Ml4OuStDoympbREURAM15', '6Gsao94MioGNcDLFGFAlw7', '1ZjqNlz7zvDQs44r6l9M3j', '6oXkzBf6bMupenvf4tKtmN', '0uQXiLK3wKmucUs9fAKx4I']` | 20 |
| `4PiJnql6Z3yQ1okaLjPHpD` | `['4OCeHEXflasM9FzPyZCb3K', '2gHf3hZx3Mihg2QqjOOAzu', '44nKzXJriXTWzrK1UVAybK', '6YWD31XpCDreL58n8R8JRm', '0gvNzwhQ3HjbjYk0q4x4wM']` | 20 |
| `1OsJZxSshQD4BCg1VtwxsN` | `['1lNeV1qtmxOGGgXN6B7cWH', '1V2CUDxo3SJnjtx6DsThg4', '0DX4vAO3I8ObqHKrw72E7f', '5b9OcWY9OSX31iaoUaQFyn', '0K6ufQj8JzIZPPkvZrEwJS']` | 20 |

---

## 5. Conclusion

**RELATED_ARTIST_GRAPH**

Kết luận: `dict_artists.json` là **related artist graph** (artist_id → related_artist_ids). Không dùng làm nguồn genre. Genre pipeline chỉ dùng `artists.csv.genres`.

| Tiêu chí | Kết quả |
|---------|---------|
| Overlap với `artists.csv.id` | 100.00% |
| Spotify ID pattern (22-char) | 100.00% |
| Sample values có phải text genre (pop/rock/...)? | Không — trông như artist IDs |

---

## 6. Impact on Database Design


- **Không dùng `dict_artists.json` làm nguồn genre.**
- Genre pipeline chỉ dùng `artists.csv.genres`.
- Bảng raw: `raw.raw_artist_json` (lưu nguyên raw values để tra cứu).
- Bảng clean (nếu dùng): `clean.artist_relations(artist_id, related_artist_id)`.
- **Không tạo `clean.artist_genres` từ `dict_artists.json`.**


---

## 7. Updated Data Contract Note

| File | Vai trò trước khi verify | Vai trò sau khi verify |
|------|--------------------------|------------------------|
| `dict_artists.json` | `unknown_need_review` | **RELATED_ARTIST_GRAPH** |
| `artists.csv.genres` | Nguồn genre chính | **Nguồn genre duy nhất được xác nhận** |
