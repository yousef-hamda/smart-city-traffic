package city.smart.ingestion.api;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Lightweight service-level health endpoint.
 *
 * <p>Complements the Spring Boot Actuator health endpoint ({@code /actuator/health}) with a
 * stable, minimal contract used by external load balancers and the platform service registry.
 */
@RestController
public class HealthController {

  private static final Map<String, String> HEALTH_BODY =
      Map.of(
          "status", "ok",
          "service", "sensor-ingestion",
          "version", "0.1.0");

  @GetMapping("/health")
  public Map<String, String> health() {
    return HEALTH_BODY;
  }
}
