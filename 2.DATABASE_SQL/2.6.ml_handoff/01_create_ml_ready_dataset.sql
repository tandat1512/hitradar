-- =============================================================================
-- Feature 1.8 — ML-Safe Dataset Handoff
-- HitRadar Pro | EPIC 1 — Data Foundation
--
-- Creates: analytics.vw_ml_ready_dataset
-- Source:  analytics.vw_ml_training_dataset (read-only projection)
--
-- RULES:
--   - CREATE OR REPLACE VIEW only — no INSERT/UPDATE/DELETE, no physical table
--   - target_popularity = LABEL (prediction target), NOT an input feature
--   - track_id = identifier for trace/debug, NOT a model input feature
--   - NO artists.popularity, NO aggregate popularity, NO popularity_bucket input
--   - NO train/test split columns
--   - NO imputed / scaled / encoded columns (EPIC 2 responsibility)
--   - NULL rows preserved (tempo, time_signature) — impute in EPIC 2
-- =============================================================================

CREATE OR REPLACE VIEW analytics.vw_ml_ready_dataset AS
SELECT
    -- Identifier — trace/debug only, do NOT use as model input
    track_id,

    -- LABEL — popularity to predict; DO NOT use as input feature
    target_popularity,

    duration_min,
    explicit,
    -- Time-sensitive features — prefer temporal split in EPIC 2
    release_year,
    release_month,
    decade,
    release_precision,

    -- Audio features (numeric inputs; scale in EPIC 2)
    danceability,
    energy,
    key,
    loudness,
    mode,
    speechiness,       -- skew/zero-inflated; consider log-transform EPIC 2
    acousticness,
    instrumentalness,  -- skew/zero-inflated; consider log-transform EPIC 2
    liveness,
    valence,
    tempo,             -- NULL allowed; impute in EPIC 2
    time_signature     -- NULL allowed; impute in EPIC 2
FROM analytics.vw_ml_training_dataset;

COMMENT ON VIEW analytics.vw_ml_ready_dataset IS
'Feature 1.8 ML-ready handoff view for EPIC 2. '
'20 columns: track_id (identifier), target_popularity (label), 18 input features. '
'No leakage columns. No imputation/scaling/encoding. '
'Source: analytics.vw_ml_training_dataset.';
