package city.smart.ingestion.service;

import city.smart.ingestion.dto.IngestionResponseDto;
import city.smart.ingestion.dto.SensorReadingDto;
import city.smart.ingestion.kafka.TrafficEventPublisher;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/**
 * Core ingestion pipeline: validates, persists to TimescaleDB, resolves road segment via PostGIS,
 * and publishes the enriched event to Kafka.
 */
@Service
public class IngestionService {

  private static final Logger log = LoggerFactory.getLogger(IngestionService.class);

  private static final String INSERT_SQL =
      "INSERT INTO traffic_readings"
          + "(time, sensor_id, segment_id, vehicle_count, avg_speed_kmh, occupancy_pct)"
          + " VALUES (?,?,?,?,?,?)";

  private final JdbcTemplate jdbc;
  private final SegmentLookupService segmentLookup;
  private final TrafficEventPublisher publisher;
  private final Counter ingestedRest;
  private final Counter ingestedMqtt;
  private final Counter ingestedGrpc;
  private final Counter rejectedCounter;

  public IngestionService(
      JdbcTemplate jdbc,
      SegmentLookupService segmentLookup,
      TrafficEventPublisher publisher,
      MeterRegistry meterRegistry) {
    this.jdbc = jdbc;
    this.segmentLookup = segmentLookup;
    this.publisher = publisher;
    this.ingestedRest =
        meterRegistry.counter("readings_ingested_total", "source", "rest");
    this.ingestedMqtt =
        meterRegistry.counter("readings_ingested_total", "source", "mqtt");
    this.ingestedGrpc =
        meterRegistry.counter("readings_ingested_total", "source", "grpc");
    this.rejectedCounter = meterRegistry.counter("readings_rejected_total");
  }

  /**
   * Ingests a batch of sensor readings from the given source (rest/mqtt/grpc). Each reading is
   * independently persisted; failures increment the rejected counter without aborting the batch.
   */
  public IngestionResponseDto ingest(List<SensorReadingDto> readings, String source) {
    long accepted = 0;
    long rejected = 0;
    String lastSegmentId = "";

    for (SensorReadingDto r : readings) {
      try {
        String segmentId =
            segmentLookup.resolveSegment(r.getSensorId(), r.getLat(), r.getLon());
        Instant ts = Instant.ofEpochSecond(r.getTs());
        jdbc.update(
            INSERT_SQL,
            Timestamp.from(ts),
            r.getSensorId(),
            segmentId.isEmpty() ? null : segmentId,
            r.getVehicleCount(),
            r.getAvgSpeedKmh(),
            r.getOccupancyPct());
        publisher.publish(segmentId, toJson(r, segmentId));
        lastSegmentId = segmentId;
        accepted++;
        counterForSource(source).increment();
      } catch (Exception e) {
        log.warn(
            "Failed to ingest reading for sensor {}: {}", r.getSensorId(), e.getMessage());
        rejected++;
        rejectedCounter.increment();
      }
    }

    return new IngestionResponseDto(accepted, rejected, lastSegmentId);
  }

  private Counter counterForSource(String source) {
    return switch (source) {
      case "mqtt" -> ingestedMqtt;
      case "grpc" -> ingestedGrpc;
      default -> ingestedRest;
    };
  }

  private String toJson(SensorReadingDto r, String segmentId) {
    return String.format(
        "{\"sensor_id\":\"%s\",\"ts\":%d,\"lat\":%f,\"lon\":%f,"
            + "\"vehicle_count\":%d,\"avg_speed_kmh\":%f,\"occupancy_pct\":%f,"
            + "\"segment_id\":\"%s\"}",
        r.getSensorId(),
        r.getTs(),
        r.getLat(),
        r.getLon(),
        r.getVehicleCount(),
        r.getAvgSpeedKmh(),
        r.getOccupancyPct(),
        segmentId);
  }
}
