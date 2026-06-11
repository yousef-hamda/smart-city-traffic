package city.smart.ingestion;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the sensor-ingestion service.
 *
 * <p>Phase 1 skeleton: boots the web server, exposes health/metrics endpoints and is
 * OpenTelemetry-ready. Phase 2 adds MQTT ingestion, PostGIS enrichment, Kafka publishing and a
 * gRPC server.
 */
@SpringBootApplication
public class Application {

  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}
