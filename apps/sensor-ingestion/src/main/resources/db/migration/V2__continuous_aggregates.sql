-- Continuous aggregates for traffic_readings.
-- Each view is wrapped in an exception handler so the migration succeeds even
-- when running against plain PostgreSQL (CI without TimescaleDB).
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN

    BEGIN
      CREATE MATERIALIZED VIEW IF NOT EXISTS traffic_readings_5min
      WITH (timescaledb.continuous) AS
      SELECT
          time_bucket('5 minutes', time) AS bucket,
          segment_id,
          SUM(vehicle_count)             AS total_vehicle_count,
          AVG(avg_speed_kmh)             AS avg_speed_kmh,
          AVG(occupancy_pct)             AS avg_occupancy_pct,
          COUNT(*)                       AS reading_count
      FROM traffic_readings
      GROUP BY bucket, segment_id
      WITH NO DATA;
    EXCEPTION WHEN OTHERS THEN
      RAISE NOTICE 'Could not create 5-min continuous aggregate: %', SQLERRM;
    END;

    BEGIN
      CREATE MATERIALIZED VIEW IF NOT EXISTS traffic_readings_1hour
      WITH (timescaledb.continuous) AS
      SELECT
          time_bucket('1 hour', time) AS bucket,
          segment_id,
          SUM(vehicle_count)          AS total_vehicle_count,
          AVG(avg_speed_kmh)          AS avg_speed_kmh,
          AVG(occupancy_pct)          AS avg_occupancy_pct,
          COUNT(*)                    AS reading_count
      FROM traffic_readings
      GROUP BY bucket, segment_id
      WITH NO DATA;
    EXCEPTION WHEN OTHERS THEN
      RAISE NOTICE 'Could not create 1-hour continuous aggregate: %', SQLERRM;
    END;

    BEGIN
      CREATE MATERIALIZED VIEW IF NOT EXISTS traffic_readings_1day
      WITH (timescaledb.continuous) AS
      SELECT
          time_bucket('1 day', time) AS bucket,
          segment_id,
          SUM(vehicle_count)         AS total_vehicle_count,
          AVG(avg_speed_kmh)         AS avg_speed_kmh,
          AVG(occupancy_pct)         AS avg_occupancy_pct,
          COUNT(*)                   AS reading_count
      FROM traffic_readings
      GROUP BY bucket, segment_id
      WITH NO DATA;
    EXCEPTION WHEN OTHERS THEN
      RAISE NOTICE 'Could not create 1-day continuous aggregate: %', SQLERRM;
    END;

  END IF;
END $$;
