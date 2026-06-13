"""PyFlink job: 5-minute tumbling average speed per road segment.

Reads enriched readings from Kafka ``traffic.raw``, computes a 5-minute
tumbling-window average speed and vehicle count per segment, and writes the
result to ``traffic.aggregates`` (which the realtime gateway fans out to the
dashboard and the Flink → Iceberg sink lands in the lake).

Run:
    flink run -py flink/windowed_speed.py
or, for local iteration:
    python flink/windowed_speed.py
"""

from pyflink.table import EnvironmentSettings, TableEnvironment

KAFKA_BOOTSTRAP = "kafka:9092"

SOURCE_DDL = f"""
CREATE TABLE traffic_raw (
    sensor_id      STRING,
    segment_id     STRING,
    vehicle_count  INT,
    avg_speed_kmh  DOUBLE,
    occupancy_pct  DOUBLE,
    `ts`           TIMESTAMP(3),
    WATERMARK FOR `ts` AS `ts` - INTERVAL '30' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'traffic.raw',
    'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
    'properties.group.id' = 'flink-windowed-speed',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601',
    'json.ignore-parse-errors' = 'true'
)
"""

SINK_DDL = f"""
CREATE TABLE traffic_aggregates (
    segment_id     STRING,
    window_start   TIMESTAMP(3),
    window_end     TIMESTAMP(3),
    avg_speed_kmh  DOUBLE,
    total_vehicles BIGINT,
    sample_count   BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'traffic.aggregates',
    'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601'
)
"""

# 5-minute tumbling window per segment over event time.
AGGREGATE_SQL = """
INSERT INTO traffic_aggregates
SELECT
    segment_id,
    window_start,
    window_end,
    AVG(avg_speed_kmh)      AS avg_speed_kmh,
    SUM(vehicle_count)      AS total_vehicles,
    COUNT(*)                AS sample_count
FROM TABLE(
    TUMBLE(TABLE traffic_raw, DESCRIPTOR(`ts`), INTERVAL '5' MINUTES)
)
WHERE segment_id IS NOT NULL
GROUP BY segment_id, window_start, window_end
"""


def main() -> None:
    env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())
    env.execute_sql(SOURCE_DDL)
    env.execute_sql(SINK_DDL)
    env.execute_sql(AGGREGATE_SQL).wait()


if __name__ == "__main__":
    main()
