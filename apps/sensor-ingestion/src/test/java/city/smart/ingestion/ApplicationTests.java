package city.smart.ingestion;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.test.context.ActiveProfiles;

/**
 * Full-context smoke test. Uses the "test" profile which substitutes an in-memory H2 datasource
 * and disables Flyway. KafkaAutoConfiguration is excluded and a {@link MockBean} satisfies the
 * {@code KafkaTemplate} dependency so the context loads without any external infrastructure. MQTT
 * and gRPC port binding are also disabled.
 */
@SpringBootTest(
    webEnvironment = WebEnvironment.RANDOM_PORT,
    properties = {
      "spring.autoconfigure.exclude="
          + "org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration",
      "spring.flyway.enabled=false",
      "spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;MODE=PostgreSQL",
      "spring.datasource.driver-class-name=org.h2.Driver",
      "spring.datasource.username=sa",
      "spring.datasource.password=",
      "ingestion.mqtt.enabled=false",
      "grpc.port=0"
    })
@ActiveProfiles("test")
class ApplicationTests {

  @MockBean
  @SuppressWarnings("rawtypes")
  KafkaTemplate kafkaTemplate;

  @Test
  void contextLoads() {
    // Verifies that all beans wire correctly without external infrastructure.
  }
}
