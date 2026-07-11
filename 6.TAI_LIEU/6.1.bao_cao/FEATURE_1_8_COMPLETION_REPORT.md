# FEATURE 1.8 COMPLETION REPORT

## 1. Feature

**Feature 1.8 — ML-Safe Dataset Handoff**

## 2. Owner

Đạt

## 3. Completed Tasks

| WBS | Task | Status |
|-----|------|--------|
| 1.8.1 | Chốt danh sách feature bàn giao cho EPIC 2 | ✅ Done |
| 1.8.2 | Tạo ml_ready_dataset dạng SQL view | ✅ Done |
| 1.8.3 | Export ml_ready_dataset dạng CSV/parquet | ✅ Done |
| 1.8.4 | Viết feature_dictionary.md | ✅ Done |
| 1.8.5 | Ghi rõ cột nào không dùng để train | ✅ Done |
| 1.8.6 | Ghi rõ rủi ro data leakage | ✅ Done |
| 1.8.7 | Ghi rõ giới hạn của popularity | ✅ Done |
| 1.8.8 | Bàn giao handoff_to_epic2.md | ✅ Done |

## 4. Outputs Created

### SQL
- `2.DATABASE_SQL/2.6.ml_handoff/01_create_ml_ready_dataset.sql`

### Scripts
- `9.SCRIPTS/export_ml_ready_dataset.py`
- `9.SCRIPTS/validate_ml_ready_dataset.py`

### Exports
- `5.DATA/processed/ml_ready_dataset.csv` (69.19 MB)
- `5.DATA/processed/ml_ready_dataset.parquet` (25.22 MB)

### Documentation
- `6.TAI_LIEU/6.1.bao_cao/feature_dictionary.md`
- `6.TAI_LIEU/6.1.bao_cao/ml_excluded_columns.md`
- `6.TAI_LIEU/6.1.bao_cao/data_leakage_risks.md`
- `6.TAI_LIEU/6.1.bao_cao/popularity_limitations.md`
- `6.TAI_LIEU/6.1.bao_cao/handoff_to_epic2.md`
- `6.TAI_LIEU/6.1.bao_cao/ML_READY_DATASET_VALIDATION_REPORT.md`

### Pipeline Guide
- `6.TAI_LIEU/6.1.bao_cao/HOW_TO_RUN_DATA_PIPELINE.md` — Feature 1.8 section added

## 5. Dataset Summary

| Property | Value |
|----------|-------|
| Source view | `analytics.vw_ml_ready_dataset` |
| Upstream | `analytics.vw_ml_training_dataset` |
| Row count | 586,672 |
| Column count | 20 |
| Label | `target_popularity` |
| Allowed input features | 18 (see handoff_to_epic2.md) |
| Non-training columns | `track_id`, `target_popularity` |
| Excluded leakage | artists.popularity, aggregate popularity, popularity_bucket, split columns, imputed/scaled columns |

## 6. Validation Summary

**Overall: PASS_WITH_WARNINGS** (2026-07-11 10:03:36 UTC)

| Check | Result |
|-------|--------|
| View exists | ✅ PASS |
| Row count = 586,672 | ✅ PASS |
| 20 required columns, no extra | ✅ PASS |
| Leakage columns | ✅ None — PASS |
| track_id null/dup | ✅ 0/0 — PASS |
| target_popularity | ✅ 0 null, min=0, max=100, zero count=44,690 — PASS |
| Data types | ✅ PASS |
| CSV export | ✅ 586,672 rows, matches DB — PASS |
| Parquet export | ✅ Created — PASS |
| Null carry-forward | ⚠️ tempo=328, time_signature=337, release_month=136,489 — WARN |

## 7. Warnings Carry-Forward (from Feature 1.7)

- `target_popularity` là label — không dùng làm input
- Popularity imbalance: ~75% tracks ≤ 40; bucket 81–100 chỉ 736 tracks
- `target_popularity = 0`: 44,690 tracks (~7.6%)
- `release_year` correlation +0.5909 với target — time bias risk
- `artists.popularity` excluded — leakage risk
- `tempo` NULL = 328 — impute EPIC 2
- `time_signature` NULL = 337 — impute EPIC 2
- `release_month` NULL = 136,489 — impute hoặc xử lý EPIC 2
- speechiness/instrumentalness skew — log-transform EPIC 2
- 4,672 track-linked genres — không one-hot toàn bộ mặc định
- Temporal split khuyến nghị EPIC 2
- Duration short=26, long=83; loudness>0=219; track_artists coverage=96.54%

## 8. EPIC 2 Recommendations

1. Temporal split theo `release_year`
2. Impute tempo (median), time_signature (mode), release_month (mode hoặc strategy riêng) — train-only fit
3. Encode release_precision, explicit
4. Scale numeric features — train-only fit
5. Log-transform speechiness, instrumentalness
6. Genre: top-N / target encoding train-only — không one-hot 4,672 genres
7. Đánh giá MAE/RMSE theo bucket và decade
8. Không thêm popularity proxy features mặc định

## 9. Final Status

### **PASS_WITH_WARNINGS**

**Lý do PASS_WITH_WARNINGS (không phải FAIL):**
- SQL view tồn tại và đúng 586,672 rows
- Export CSV + Parquet thành công
- Không có leakage columns
- Documentation đầy đủ
- Carry-forward warnings:
  - tempo NULL = 328
  - time_signature NULL = 337
  - release_month NULL = 136,489
  - popularity imbalance (~75% tracks ≤ 40)
  - target_popularity = 0: 44,690

**Đủ điều kiện đóng Feature 1.8:** ✅ **Có** — sẵn sàng bàn giao EPIC 2

---

*Feature 1.8 — ML-Safe Dataset Handoff | HitRadar Pro | 2026-07-11*
