package city.smart.ingestion;

import static org.assertj.core.api.Assertions.assertThat;

import city.smart.ingestion.dto.SensorReadingDto;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

/**
 * Full-stack integration test using Testcontainers. Automatically skipped when Docker is not
 * available ({@code @Testcontainers(disabledWithoutDocker = true)}).
 */
@Testcontainers(disabledWithoutDocker = true)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    properties = {"ingestion.mqtt.enabled=false", "grpc.port=0"})
class IngestionIntegrationTest {

  @Container
  static PostgreSQLContainer<?> postgres =
      new PostgreSQLContainer<>(
              DockerImageName.parse("timescale/timescaledb-ha:pg16")
                  .asCompatibleSubstituteFor("postgres"))
          .withDatabaseName("smartcity")
          .withUsername("smartcity")
          .withPassword("smartcity");

  @Container
  static KafkaContainer kafka =
      new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.4.0"));

  @DynamicPropertySource
  static void registerProps(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
    registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
  }

  @Autowired private TestRestTemplate restTemplate;
  @Autowired private JdbcTemplate jdbc;
  @Autowired private ObjectMapper objectMapper;

  @Test
  @SuppressWarnings("unchecked")
  void bulkReadingsPersistedAndSegmentResolved() throws Exception {
    // Seed a road segment close to the test coordinates
    jdbc.update(
        "INSERT INTO road_segments(id, name, geometry)"
            + " VALUES (?,?,ST_SetSRID(ST_MakeLine("
            + "ST_MakePoint(35.2,31.7),ST_MakePoint(35.3,31.8)),4326))",
        "seg-001",
        "Test Road");
    jdbc.update(
        "INSERT INTO sensors(id, segment_id, location)"
            + " VALUES (?,?,ST_SetSRID(ST_MakePoint(35.21,31.71),4326))",
        "sensor-001",
        "seg-001");

    List<SensorReadingDto> dtos = List.of(reading("sensor-001"), reading("sensor-002"));
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    HttpEntity<String> request =
        new HttpEntity<>(objectMapper.writeValueAsString(dtos), headers);

    ResponseEntity<Map> response =
        restTemplate.postForEntity("/api/v1/readings/bulk", request, Map.class);

    assertThat(response.getStatusCode()).isEqualTo(HttpStatus.ACCEPTED);
    assertThat((Integer) response.getBody().get("accepted")).isEqualTo(2);

    Integer count =
        jdbc.queryForObject("SELECT COUNT(*) FROM traffic_readings", Integer.class);
    assertThat(count).isEqualTo(2);

    String segId =
        jdbc.queryForObject(
            "SELECT segment_id FROM traffic_readings WHERE sensor_id='sensor-001'",
            String.class);
    assertThat(segId).isEqualTo("seg-001");
  }

  private SensorReadingDto reading(String sensorId) {
    SensorReadingDto dto = new SensorReadingDto();
    dto.setSensorId(sensorId);
    dto.setTs(System.currentTimeMillis() / 1000);
    dto.setLat(31.71);
    dto.setLon(35.21);
    dto.setVehicleCount(5);
    dto.setAvgSpeedKmh(40.0);
    dto.setOccupancyPct(20.0);
    return dto;
  }
}
