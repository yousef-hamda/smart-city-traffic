package city.smart.ingestion.api;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import city.smart.ingestion.dto.IngestionResponseDto;
import city.smart.ingestion.dto.SensorReadingDto;
import city.smart.ingestion.service.IngestionService;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

/** Slice test for {@link ReadingController}. Infrastructure is fully mocked. */
@WebMvcTest(ReadingController.class)
class ReadingControllerTest {

  @Autowired private MockMvc mockMvc;
  @Autowired private ObjectMapper objectMapper;
  @MockBean private IngestionService ingestionService;

  @Test
  void singleReadingReturns202() throws Exception {
    when(ingestionService.ingest(any(), anyString()))
        .thenReturn(new IngestionResponseDto(1, 0, "seg-001"));

    mockMvc
        .perform(
            post("/api/v1/readings")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(validDto())))
        .andExpect(status().isAccepted())
        .andExpect(jsonPath("$.accepted").value(1))
        .andExpect(jsonPath("$.rejected").value(0))
        .andExpect(jsonPath("$.road_segment_id").value("seg-001"));
  }

  @Test
  void invalidReadingReturns400() throws Exception {
    // sensor_id is blank, vehicle_count is negative — both fail validation
    String invalidJson =
        "{\"sensor_id\":\"\",\"ts\":1000,\"lat\":0,\"lon\":0,"
            + "\"vehicle_count\":-1,\"avg_speed_kmh\":0,\"occupancy_pct\":0}";

    mockMvc
        .perform(
            post("/api/v1/readings")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidJson))
        .andExpect(status().isBadRequest());
  }

  @Test
  void bulkReadingReturns202() throws Exception {
    when(ingestionService.ingest(any(), anyString()))
        .thenReturn(new IngestionResponseDto(2, 0, "seg-001"));

    List<SensorReadingDto> dtos = List.of(validDto(), validDto());
    mockMvc
        .perform(
            post("/api/v1/readings/bulk")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(dtos)))
        .andExpect(status().isAccepted())
        .andExpect(jsonPath("$.accepted").value(2));
  }

  private SensorReadingDto validDto() {
    SensorReadingDto dto = new SensorReadingDto();
    dto.setSensorId("sensor-001");
    dto.setTs(System.currentTimeMillis() / 1000);
    dto.setLat(31.7683);
    dto.setLon(35.2137);
    dto.setVehicleCount(10);
    dto.setAvgSpeedKmh(50.0);
    dto.setOccupancyPct(30.0);
    return dto;
  }
}
