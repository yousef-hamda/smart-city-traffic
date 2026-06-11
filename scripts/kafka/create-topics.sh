#!/usr/bin/env bash
# Creates every Kafka topic the platform uses. Idempotent — safe to re-run.
set -euo pipefail

BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}"
KAFKA_TOPICS="/opt/kafka/bin/kafka-topics.sh"

# topic:partitions:retention_ms
TOPICS=(
  "traffic.raw:6:86400000"
  "traffic.aggregates:6:604800000"
  "traffic.events:6:86400000"
  "vision.frames:6:3600000"
  "vision.events:6:86400000"
  "predictions:3:86400000"
  "signal.recommendations:3:86400000"
  "alerts:3:604800000"
)

for entry in "${TOPICS[@]}"; do
  IFS=':' read -r topic partitions retention <<<"$entry"
  "$KAFKA_TOPICS" --bootstrap-server "$BOOTSTRAP" \
    --create --if-not-exists \
    --topic "$topic" \
    --partitions "$partitions" \
    --replication-factor 1 \
    --config "retention.ms=$retention"
done

echo "Kafka topics ready:"
"$KAFKA_TOPICS" --bootstrap-server "$BOOTSTRAP" --list
