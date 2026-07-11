# EPIC 1 SPRINT REVIEW DEMO — HITRADAR PRO

**Project:** HitRadar Pro  
**EPIC:** 1 — Data Foundation & Data Understanding  
**Owner:** Đạt  
**Demo duration:** ~5 minutes  
**Date prepared:** 2026-07-11

---

## 1. Demo Goal

Trình bày cho stakeholder/reviewer rằng EPIC 1 đã:

1. Xác định và audit dataset thực tế (không phải old 5 CSV).
2. Xây dựng pipeline reproducible: Raw → Clean → Analytics → ML-ready.
3. Thực hiện EDA có bằng chứng (6 notebooks, 42 cells, 0 errors).
4. Bàn giao ML-safe dataset cho EPIC 2 với documentation đầy đủ.

---

## 2. 5-Minute Demo Script

### Minute 0–1: Context & Dataset

> "HitRadar Pro EPIC 1 xây nền tảng dữ liệu cho dự đoán popularity Spotify.
>
> Dataset thực tế gồm **3 files**: tracks.csv (586,672 bài), artists.csv (1.16M nghệ sĩ), và dict_artists.json (related artist graph — **không phải genre**).
>
> Chúng tôi **không dùng** old 5 CSV aggregate files — scope đã lock ở Feature 1.0."

### Minute 1–2: Pipeline

> "Pipeline 4 tầng:
> - **Raw**: import nguyên bản, không transform
> - **Clean**: parse list-strings, normalize release dates, FK validate
> - **Analytics**: 10 views cho EDA và monitoring
> - **ML-ready**: 20 columns, no leakage, export CSV/Parquet
>
> Toàn bộ reproducible qua HOW_TO_RUN_DATA_PIPELINE.md."

### Minute 2–3: Data Quality & Warnings

> "Quality gates: **12 gates, 0 FAIL**, PASS_WITH_WARNINGS.
>
> Warnings chính — **không phải lỗi**, là carry-forward cho EPIC 2:
> - tempo/time_signature NULL (328/337)
> - release_month NULL (136K — year-only releases)
> - popularity imbalance (~75% tracks ≤ 40)
> - track_artists coverage 96.54%"

### Minute 3–4: EDA Highlights

> "6 EDA notebooks đã **execute thật**: 42/42 cells, 0 errors, 16 charts.
>
> Insight chính:
> - release_year correlation **+0.59** với popularity → time bias risk
> - acousticness giảm theo thời gian (nhạc điện tử tăng)
> - 4,672 genres — không one-hot toàn bộ
> - Khuyến nghị EPIC 2: **temporal split**, không random split"

### Minute 4–5: ML Handoff

> "Feature 1.8 bàn giao:
> - View: `analytics.vw_ml_ready_dataset` — 586,672 rows, 20 cols
> - Label: target_popularity
> - 18 input features, **no leakage columns**
> - Export: CSV + Parquet
> - Docs: handoff_to_epic2.md, leakage risks, popularity limitations
>
> **Status: PASS_WITH_WARNINGS — sẵn sàng EPIC 2.**"

---

## 3. Demo Flow

| Step | Action | What to show |
|------|--------|--------------|
| 1 | Show project folder | `1.DỮ_LIỆU/`, `2.DATABASE_SQL/`, `3.NOTEBOOKS/`, `5.DATA/`, `6.TAI_LIEU/` |
| 2 | Show schema layers | `DATABASE_SCHEMA.md` — raw/clean/analytics diagram |
| 3 | Show row counts | SQL queries (section 4) |
| 4 | Show analytics views | `ANALYTICS_VIEWS_REPORT.md` or `vw_data_quality_report` |
| 5 | Show EDA findings | `EDA_FINDINGS.md` — popularity buckets, correlation |
| 6 | Show ML dataset | `vw_ml_ready_dataset LIMIT 5` + export file sizes |
| 7 | Show handoff | `handoff_to_epic2.md` — allowed features, excluded, warnings |

---

## 4. SQL Queries for Demo

```sql
-- Row counts
SELECT COUNT(*) FROM clean.tracks;
-- Expected: 586672

SELECT COUNT(*) FROM analytics.vw_ml_ready_dataset;
-- Expected: 586672

-- Data quality snapshot
SELECT * FROM analytics.vw_data_quality_report;

-- ML-ready sample (no leakage columns)
SELECT track_id, target_popularity, duration_min, explicit,
       release_year, danceability, energy, tempo
FROM analytics.vw_ml_ready_dataset
LIMIT 5;

-- Popularity distribution
SELECT * FROM analytics.vw_popularity_stats;
```

---

## 5. Key Talking Points

| Topic | Number / Fact |
|-------|---------------|
| Tracks | 586,672 |
| Artists (total) | 1,162,095 |
| Artists with tracks | 81,776 |
| Genres (total) | 5,366 |
| Track-linked genres | 4,672 |
| ML-ready columns | 20 (18 input + label + id) |
| Leakage columns | 0 |
| EDA notebooks | 6/6 executed, 0 errors |
| Quality gates FAIL | 0 |
| EPIC 1 status | PASS_WITH_WARNINGS |
| EPIC 2 split | Temporal by release_year (recommended) |

---

## 6. Possible Questions & Answers

### Q: Vì sao PASS_WITH_WARNINGS mà không PASS?

**A:** Tất cả checks critical đều pass (0 FAIL). Warnings là carry-forward có chủ đích: NULLs chưa impute (thuộc EPIC 2), popularity imbalance, time bias. EPIC 1 cố ý không impute/scale để tránh leakage.

### Q: Vì sao không train model ở EPIC 1?

**A:** EPIC 1 scope = data foundation only. Train/test split, imputation, scaling phải fit on train only — thuộc EPIC 2. EPIC 1 chỉ deliver clean data + ML-safe handoff.

### Q: Vì sao không dùng artists.popularity?

**A:** Leakage risk — artist popularity là proxy rất mạnh của track popularity. Đã exclude khỏi `vw_ml_ready_dataset`. Xem `data_leakage_risks.md`.

### Q: Vì sao release_year nguy hiểm?

**A:** Correlation +0.5909 với target. Spotify popularity phụ thuộc streams gần đây → tracks mới có lợi thế. Random split khiến model học time bias. Khuyến nghị temporal split.

### Q: Vì sao popularity không phải chất lượng âm nhạc?

**A:** Popularity = proxy nhu cầu trên Spotify tại thời điểm snapshot — phụ thuộc playlist, marketing, thời gian phát hành. Xem `popularity_limitations.md`.

### Q: Vì sao genre không one-hot toàn bộ?

**A:** 4,672 track-linked genres — quá nhiều dimensions, sparse, long-tail. EPIC 2 nên dùng top-N, embedding, hoặc target encoding (fit on train only).

### Q: dict_artists.json dùng để làm gì?

**A:** Related artist graph → `clean.artist_relations` (8.86M edges). **Không phải genre source.** Genre chỉ từ `artists.csv.genres`.

---

*Feature 1.9 — Documentation & Epic Review | HitRadar Pro*
