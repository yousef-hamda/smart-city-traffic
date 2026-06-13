"""PyFlink job: high-confidence incident detection by joining two streams.

Complex-event-processing-style correlation: a real incident usually shows up in
*both* modalities within a short window — a sharp speed drop on a segment
(``traffic.raw``) AND a stopped/abnormal vehicle from the camera feed
(``vision.events``) on the same segment within 60 seconds. Correlating the two
yields far fewer false positives than either stream alone.

Matches are written to ``alerts`` as high-confidence incidents.

Run:
    flink run -py flink/cep_incidents.py
"""

from pyflink.table import EnvironmentSettings, TableEnvironment

KAFKA_BOOTSTRAP = "kafka:9092"

TRAFFIC_DDL = f"""
CREATE TABLE traffic_raw (
    segment_id     STRING,
    avg_speed_kmh  DOUBLE,
    `ts`           TIMESTAMP(3),
    WATERMARK FOR `ts` AS `ts` - INTERVAL '30' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'traffic.raw',
    'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
    'properties.group.id' = 'flink-cep-traffic',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601',
    'json.ignore-parse-errors' = 'true'
)
"""

VISION_DDL = f"""
CREATE TABLE vision_events (
    segment_id  STRING,
    incidents   ARRAY<ROW<kind STRING, track_id INT>>,
    `ts`        TIMESTAMP(3),
    WATERMARK FOR `ts` AS `ts` - INTERVAL '30' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'vision.events',
    'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
    'properties.group.id' = 'flink-cep-vision',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601',
    'json.ignore-parse-errors' = 'true'
)
"""

ALERTS_DDL = f"""
CREATE TABLE alerts_sink (
    segment_id  STRING,
    alert_type  STRING,
    severity    STRING,
    message     STRING,
    `ts`        TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'alerts',
    'properties.bootstrap.servers' = '{KAFKA_BOOTSTRAP}',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601'
)
"""

# Speed drop (< 12 km/h) on a segment within 60s of a camera-detected stopped
# vehicle on the same segment → high-confidence incident.
CEP_SQL = """
INSERT INTO alerts_sink
SELECT
    t.segment_id,
    'incident' AS alert_type,
    'high'     AS severity,
    'Corroborated incident: speed drop + camera-detected stopped vehicle' AS message,
    t.`ts`     AS `ts`
FROM traffic_raw AS t
JOIN vision_events AS v
  ON t.segment_id = v.segment_id
 AND t.`ts` BETWEEN v.`ts` - INTERVAL '60' SECOND AND v.`ts` + INTERVAL '60' SECOND
WHERE t.avg_speed_kmh < 12.0
  AND EXISTS (
      SELECT 1 FROM UNNEST(v.incidents) AS i(kind, track_id)
      WHERE i.kind = 'stopped_vehicle'
  )
"""


def main() -> None:
    env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())
    env.execute_sql(TRAFFIC_DDL)
    env.execute_sql(VISION_DDL)
    env.execute_sql(ALERTS_DDL)
    env.execute_sql(CEP_SQL).wait()


if __name__ == "__main__":
    main()
