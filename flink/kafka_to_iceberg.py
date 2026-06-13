"""PyFlink job: land raw Kafka streams into Apache Iceberg tables on MinIO.

This is the lake's raw layer. ``traffic.raw`` and ``vision.events`` are written
to Iceberg tables (``raw.readings``, ``raw.vision_events``) in the MinIO bucket;
dbt (via Trino) then transforms raw → staging → marts. Iceberg gives the lake
ACID tables, schema evolution, and time travel over object storage.

Run (needs the Iceberg + S3 Flink connectors on the classpath):
    flink run -py flink/kafka_to_iceberg.py
"""

from pyflink.table import EnvironmentSettings, TableEnvironment

KAFKA_BOOTSTRAP = "kafka:9092"
MINIO_ENDPOINT = "http://minio:9000"

# Iceberg catalog backed by MinIO (S3-compatible) with a Hadoop/REST catalog.
ICEBERG_CATALOG_DDL = f"""
CREATE CATALOG iceberg WITH (
    'type' = 'iceberg',
    'catalog-type' = 'hadoop',
    'warehouse' = 's3a://traffic-lake/warehouse',
    's3.endpoint' = '{MINIO_ENDPOINT}',
    's3.path-style-access' = 'true',
    's3.access-key-id' = 'traffic',
    's3.secret-access-key' = 'traffic_dev_password'
)
"""

READINGS_SOURCE_DDL = f"""
CREATE TEMPORARY TABLE traffic_raw_src (
    sensor_id      STRING,
    segment_id     STRING,
    vehicle_count  INT,
    avg_speed_kmh  DOUBLE,
    occupancy_pct  DOUBLE,
    `ts`           TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'traffic.raw',
    'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
    'properties.group.id' = 'flink-iceberg-readings',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601',
    'json.ignore-parse-errors' = 'true'
)
"""

CREATE_RAW_READINGS = """
CREATE TABLE IF NOT EXISTS iceberg.raw.readings (
    sensor_id      STRING,
    segment_id     STRING,
    vehicle_count  INT,
    avg_speed_kmh  DOUBLE,
    occupancy_pct  DOUBLE,
    event_time     TIMESTAMP(3)
) PARTITIONED BY (segment_id)
"""

SINK_READINGS = """
INSERT INTO iceberg.raw.readings
SELECT sensor_id, segment_id, vehicle_count, avg_speed_kmh, occupancy_pct, `ts`
FROM traffic_raw_src
"""


def main() -> None:
    env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())
    env.execute_sql(ICEBERG_CATALOG_DDL)
    env.execute_sql("CREATE DATABASE IF NOT EXISTS iceberg.raw")
    env.execute_sql(CREATE_RAW_READINGS)
    env.execute_sql(READINGS_SOURCE_DDL)
    env.execute_sql(SINK_READINGS).wait()


if __name__ == "__main__":
    main()
