-- Canonical platform schema. Flyway (owned by sensor-ingestion) is the single
-- source of truth for the shared Postgres database; other services consume it
-- via typed clients (the API gateway generates a Prisma client by introspection
-- rather than running a second migration tool against the same DB). See
-- docs/adr/0006-single-schema-owner.md.

-- Extensions (require superuser; idempotent)
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Neighborhoods (trilingual names: en / he / ar)
CREATE TABLE IF NOT EXISTS neighborhoods (
    id      TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name_en TEXT NOT NULL,
    name_he TEXT,
    name_ar TEXT,
    polygon geometry(Polygon, 4326)
);

-- Road segments (trilingual names; road_id/seq tie back to the source polyline)
CREATE TABLE IF NOT EXISTS road_segments (
    id               TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    road_id          TEXT,
    seq              INTEGER,
    name_en          TEXT,
    name_he          TEXT,
    name_ar          TEXT,
    segment_type     TEXT,
    speed_limit_kmh  INTEGER,
    lanes            INTEGER,
    neighborhood_id  TEXT REFERENCES neighborhoods (id),
    geometry         geometry(LineString, 4326)
);
CREATE INDEX IF NOT EXISTS road_segments_geom_idx ON road_segments USING GIST (geometry);

-- Sensors
CREATE TABLE IF NOT EXISTS sensors (
    id           TEXT PRIMARY KEY,
    sensor_type  TEXT,
    segment_id   TEXT REFERENCES road_segments (id),
    location     geometry(Point, 4326),
    installed_at TIMESTAMPTZ DEFAULT NOW(),
    active       BOOLEAN     DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS sensors_geom_idx ON sensors USING GIST (location);

-- Cameras
CREATE TABLE IF NOT EXISTS cameras (
    id                TEXT PRIMARY KEY,
    segment_id        TEXT REFERENCES road_segments (id),
    location          geometry(Point, 4326),
    rtsp_url          TEXT,
    direction_degrees INTEGER,
    active            BOOLEAN DEFAULT TRUE
);

-- Traffic readings (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS traffic_readings (
    time           TIMESTAMPTZ       NOT NULL,
    sensor_id      TEXT              NOT NULL,
    segment_id     TEXT,
    vehicle_count  INTEGER,
    avg_speed_kmh  DOUBLE PRECISION,
    occupancy_pct  DOUBLE PRECISION
);
SELECT create_hypertable('traffic_readings', 'time', if_not_exists => TRUE);

-- Vision events (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS vision_events (
    time        TIMESTAMPTZ      NOT NULL,
    camera_id   TEXT             NOT NULL,
    segment_id  TEXT,
    event_type  TEXT,
    confidence  DOUBLE PRECISION,
    payload     JSONB
);
SELECT create_hypertable('vision_events', 'time', if_not_exists => TRUE);

-- Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id                         TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    segment_id                 TEXT REFERENCES road_segments (id),
    predicted_at               TIMESTAMPTZ DEFAULT NOW(),
    prediction_horizon_minutes INTEGER,
    predicted_vehicle_count    INTEGER,
    predicted_avg_speed_kmh    DOUBLE PRECISION,
    lower_ci                   DOUBLE PRECISION,
    upper_ci                   DOUBLE PRECISION,
    shap_top5                  JSONB,
    model_version              TEXT
);

-- Signal recommendations
CREATE TABLE IF NOT EXISTS signal_recommendations (
    id                     TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    intersection_id        TEXT,
    segment_id             TEXT REFERENCES road_segments (id),
    recommended_at         TIMESTAMPTZ DEFAULT NOW(),
    phase_timings          JSONB,
    expected_throughput    DOUBLE PRECISION,
    agent_version          TEXT
);

-- Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id               TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    segment_id       TEXT REFERENCES road_segments (id),
    incident_type    TEXT,
    severity         TEXT,
    source           TEXT,
    reporter_user_id TEXT,
    detected_at      TIMESTAMPTZ DEFAULT NOW(),
    resolved_at      TIMESTAMPTZ,
    description      TEXT
);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    segment_id      TEXT,
    alert_type      TEXT,
    severity        TEXT,
    message         TEXT,
    payload         JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ
);

-- Users (identity; auth is enforced by the API gateway)
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'viewer',
    locale        TEXT NOT NULL DEFAULT 'en',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Refresh tokens (rotating; revoked on rotation/logout)
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id         TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id    TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS refresh_tokens_user_idx ON refresh_tokens (user_id);

-- API keys (scoped, per-key quota for the developer portal)
CREATE TABLE IF NOT EXISTS api_keys (
    id               TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id          TEXT REFERENCES users (id) ON DELETE CASCADE,
    key_hash         TEXT        NOT NULL UNIQUE,
    name             TEXT,
    scopes           JSONB       DEFAULT '[]'::jsonb,
    quota_per_minute INTEGER     DEFAULT 60,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    expires_at       TIMESTAMPTZ,
    active           BOOLEAN     DEFAULT TRUE
);

-- API usage (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS api_usage (
    time             TIMESTAMPTZ NOT NULL,
    api_key_id       TEXT REFERENCES api_keys (id),
    endpoint         TEXT,
    method           TEXT,
    status_code      INTEGER,
    response_time_ms INTEGER
);
SELECT create_hypertable('api_usage', 'time', if_not_exists => TRUE);
