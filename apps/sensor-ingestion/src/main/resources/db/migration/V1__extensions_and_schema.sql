-- Extensions (require superuser; idempotent)
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Neighborhoods
CREATE TABLE IF NOT EXISTS neighborhoods (
    id      TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name    TEXT NOT NULL,
    polygon geometry(Polygon, 4326)
);

-- Road segments
CREATE TABLE IF NOT EXISTS road_segments (
    id               TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name             TEXT,
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
    model_version              TEXT
);

-- Signal recommendations
CREATE TABLE IF NOT EXISTS signal_recommendations (
    id                     TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    intersection_id        TEXT,
    segment_id             TEXT REFERENCES road_segments (id),
    recommended_at         TIMESTAMPTZ DEFAULT NOW(),
    green_duration_seconds INTEGER,
    red_duration_seconds   INTEGER,
    algorithm              TEXT
);

-- Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    segment_id    TEXT REFERENCES road_segments (id),
    incident_type TEXT,
    severity      TEXT,
    detected_at   TIMESTAMPTZ DEFAULT NOW(),
    resolved_at   TIMESTAMPTZ,
    description   TEXT
);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    segment_id      TEXT,
    alert_type      TEXT,
    severity        TEXT,
    message         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ
);

-- API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id           TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    key_hash     TEXT        NOT NULL UNIQUE,
    name         TEXT,
    owner_email  TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    expires_at   TIMESTAMPTZ,
    active       BOOLEAN     DEFAULT TRUE
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
