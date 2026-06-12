package city.smart.ingestion.dto;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import org.junit.jupiter.api.Test;

/** Verifies snake_case serialisation round-trip for {@link SensorReadingDto}. */
class SensorReadingDtoTest {

  private final ObjectMapper mapper =
      new ObjectMapper().setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);

  @Test
  void snakeCaseRoundTrip() throws Exception {
    String json =
        "{\"sensor_id\":\"s1\",\"ts\":1000,\"lat\":31.7,\"lon\":35.2,"
            + "\"vehicle_count\":5,\"avg_speed_kmh\":40.0,\"occupancy_pct\":20.0}";

    SensorReadingDto dto = mapper.readValue(json, SensorReadingDto.class);

    assertThat(dto.getSensorId()).isEqualTo("s1");
    assertThat(dto.getVehicleCount()).isEqualTo(5);
    assertThat(dto.getAvgSpeedKmh()).isEqualTo(40.0);

    String out = mapper.writeValueAsString(dto);
    assertThat(out).contains("sensor_id");
    assertThat(out).contains("vehicle_count");
    assertThat(out).contains("avg_speed_kmh");
  }
}
