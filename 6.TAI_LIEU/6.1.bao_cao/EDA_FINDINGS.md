# EDA FINDINGS — HITRADAR PRO EPIC 1

**Project:** HitRadar Pro  
**Feature:** 1.7 EDA + 1.9 Documentation synthesis  
**Owner:** Đạt  
**Status:** Final  
**Sources:** EDA_INSIGHTS_REPORT.md, EDA_NOTEBOOK_VALIDATION_REPORT.md, Feature 1.7 completion report

---

## 1. Purpose

Tóm tắt insight khám phá dữ liệu từ Feature 1.7 — phục vụ Sprint Review, EPIC 2 planning, và documentation final. Mọi số liệu có nguồn từ notebooks đã execute và analytics views.

---

## 2. Notebook Evidence

| Metric | Value | Source |
|--------|-------|--------|
| Notebooks executed | **6/6** | EDA_NOTEBOOK_VALIDATION_REPORT.md |
| Code cells executed | **42/42** | EDA_NOTEBOOK_VALIDATION_REPORT.md |
| Errors | **0** | EDA_NOTEBOOK_VALIDATION_REPORT.md |
| Charts generated | **16** | EDA_NOTEBOOK_VALIDATION_REPORT.md |
| Outputs | **53** | EDA_NOTEBOOK_VALIDATION_REPORT.md |
| Overall notebook status | PASS | EDA_NOTEBOOK_VALIDATION_REPORT.md |

**Notebooks:** `3.NOTEBOOKS/3.4.eda/01`–`06` (overview, popularity, audio, time/decade, artist/genre, correlation/outlier)

---

## 3. Dataset Scale

| Metric | Value |
|--------|-------|
| Total tracks | 586,672 |
| Artists with tracks | 81,776 |
| Total artists in DB | 1,162,095 |
| `clean.genres` (total) | 5,366 |
| Track-linked genres | 4,672 |
| Release years observed | 1921–2021 (101 years) |
| Decades | 12 (1900–2020) |
| Decade with most tracks | 1990s (108,875) |

---

## 4. Popularity Findings

- **~75% tracks có popularity ≤ 40** (heavy low tail).
- Bucket **81–100** chỉ **736 tracks** (0.1%).
- **target_popularity = 0:** 44,690 tracks (~7.6%) — inactive/unlisted, không phải lỗi dữ liệu.
- **Popularity là proxy** thành công trên Spotify tại thời điểm snapshot — **không phải chất lượng âm nhạc**.
- Bucket distribution:

| Bucket | Count |
|--------|-------|
| 0–20 | 219,988 |
| 21–40 | 219,003 |
| 41–60 | 122,813 |
| 61–80 | 24,132 |
| 81–100 | 736 |

---

## 5. Time Bias Findings

- **`release_year` correlation +0.5909** với `target_popularity` — predictor mạnh nhất.
- Popularity tăng theo thời gian: 1920s avg ≈ 1 → 2020s avg ≈ 42 (streams/activity gần đây).
- **Random split có rủi ro** — model có thể học time bias thay vì audio signal.
- **Khuyến nghị EPIC 2:** temporal split theo `release_year`.
- Dataset mất cân bằng thời gian: 1990s + 2010s ≈ 36% tổng; 1920s sparse (~1.3%).

---

## 6. Audio Feature Findings

| Feature | Mean | Note |
|---------|------|------|
| danceability | 0.564 | Phân bố đều |
| energy | 0.542 | Phù hợp ML |
| speechiness | 0.105 | Skew/zero-inflated → log-transform EPIC 2 |
| acousticness | 0.450 | Bimodal; corr −0.37 với target |
| instrumentalness | 0.114 | Skew/zero-inflated |
| liveness | 0.214 | Lệch phải |
| valence | 0.552 | Tương đối đều |

**Correlations với target (top):** release_year +0.59, loudness +0.33, energy +0.30, acousticness −0.37, instrumentalness −0.24.

**NULLs:** tempo=328, time_signature=337 — impute EPIC 2.

**Time trend:** acousticness giảm ~0.90 (1920s) → ~0.28 (2020s).

---

## 7. Artist/Genre Findings

- **Top genres:** rock (32,026), adult standards (26,688), classic rock (23,808), filmi (19,557), classical (18,995).
- **Genre long-tail:** 4,672 track-linked genres — **không one-hot toàn bộ** mặc định.
- **Artist bias:** long-tail distribution; top artists include international content (e.g. Die drei ???, Lata Mangeshkar).
- **track_artists coverage:** 96.54% — 26,224 tracks thiếu artist link.
- **Genre gap:** 694 genres (5,366 − 4,672) thuộc artists bị skip — không phải lỗi data.

---

## 8. Outliers

| Type | Count | % |
|------|-------|---|
| Duration short (<10s) | 26 | 0.004% |
| Duration long (>60min) | 83 | 0.014% |
| Loudness > 0 dB | 219 | 0.037% |
| Tempo NULL | 328 | 0.056% |
| Time_signature NULL | 337 | 0.057% |

Outliers **giữ theo rule F1.4** — không drop trong EPIC 1.

---

## 9. ML Implications

| Action | Owner |
|--------|-------|
| Impute tempo, time_signature, release_month | EPIC 2 (train-only fit) |
| Scale numeric features | EPIC 2 (train-only fit) |
| Log-transform speechiness, instrumentalness | EPIC 2 |
| Encode release_precision, explicit | EPIC 2 |
| Temporal split | EPIC 2 (recommended) |
| Genre encoding (top-N / embedding / target encoding) | EPIC 2 (train-only fit) |
| Avoid leakage (target, artists.popularity, global stats) | EPIC 2 |
| Evaluate by popularity bucket and decade | EPIC 2 |

**EPIC 1 delivered:** `analytics.vw_ml_ready_dataset` + handoff docs — no imputation, scaling, encoding, or train/test split.

---

*Feature 1.9 — Documentation & Epic Review | HitRadar Pro*
