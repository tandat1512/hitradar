-- =============================================================
-- 01_create_schemas.sql
-- HitRadar — tạo 3 schema chính
-- Feature 1.2 — Database Architecture
-- =============================================================

-- Raw layer: dữ liệu import nguyên bản từ CSV/JSON
CREATE SCHEMA IF NOT EXISTS raw;

-- Clean layer: dữ liệu đã parse, normalize, enforce constraints
CREATE SCHEMA IF NOT EXISTS clean;

-- Analytics layer: views / marts phục vụ EDA, dashboard, ML handoff
CREATE SCHEMA IF NOT EXISTS analytics;
