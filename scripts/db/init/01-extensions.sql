-- Runs once on first Postgres boot (docker-entrypoint-initdb.d).
-- TimescaleDB + PostGIS are the storage backbone for all time-series and
-- geospatial data; schema migrations are owned by each service (Prisma /
-- Flyway), this file only guarantees the extensions exist.
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
