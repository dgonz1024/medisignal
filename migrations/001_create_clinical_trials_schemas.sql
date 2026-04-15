CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS raw.study_records (
    id BIGSERIAL PRIMARY KEY,
    nct_id VARCHAR(32) NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_hash VARCHAR(64) NOT NULL,
    payload_jsonb JSONB NOT NULL,
    CONSTRAINT uq_raw_study_records_nct_id_source_hash UNIQUE (nct_id, source_hash)
);

CREATE INDEX IF NOT EXISTS ix_raw_study_records_nct_id ON raw.study_records (nct_id);

CREATE TABLE IF NOT EXISTS staging.studies (
    nct_id VARCHAR(32) PRIMARY KEY,
    brief_title TEXT,
    official_title TEXT,
    study_type VARCHAR(100),
    phase VARCHAR(50),
    overall_status VARCHAR(100),
    start_date DATE,
    completion_date DATE,
    enrollment_count INTEGER,
    healthy_volunteers BOOLEAN,
    sex VARCHAR(50),
    minimum_age VARCHAR(50),
    maximum_age VARCHAR(50),
    sponsor_name VARCHAR(255),
    last_update_posted DATE
);

CREATE TABLE IF NOT EXISTS staging.conditions (
    id BIGSERIAL PRIMARY KEY,
    nct_id VARCHAR(32) NOT NULL,
    condition_name VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_staging_conditions_nct_id ON staging.conditions (nct_id);

CREATE TABLE IF NOT EXISTS staging.interventions (
    id BIGSERIAL PRIMARY KEY,
    nct_id VARCHAR(32) NOT NULL,
    intervention_type VARCHAR(100),
    intervention_name VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_staging_interventions_nct_id ON staging.interventions (nct_id);

CREATE TABLE IF NOT EXISTS staging.locations (
    id BIGSERIAL PRIMARY KEY,
    nct_id VARCHAR(32) NOT NULL,
    facility VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS ix_staging_locations_nct_id ON staging.locations (nct_id);

CREATE TABLE IF NOT EXISTS analytics.trial_summary (
    nct_id VARCHAR(32) PRIMARY KEY,
    phase VARCHAR(50),
    status VARCHAR(100),
    enrollment_count INTEGER,
    location_count INTEGER,
    condition_count INTEGER,
    sponsor_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS analytics.condition_stats (
    condition_name VARCHAR(255) PRIMARY KEY,
    trial_count INTEGER NOT NULL,
    avg_enrollment NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS analytics.sponsor_stats (
    sponsor_name VARCHAR(255) PRIMARY KEY,
    trial_count INTEGER NOT NULL,
    completion_rate NUMERIC(5, 2)
);

CREATE TABLE IF NOT EXISTS analytics.quality_issues (
    id BIGSERIAL PRIMARY KEY,
    nct_id VARCHAR(32) NOT NULL,
    issue_type VARCHAR(100) NOT NULL,
    issue_description TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_analytics_quality_issues_nct_id ON analytics.quality_issues (nct_id);

