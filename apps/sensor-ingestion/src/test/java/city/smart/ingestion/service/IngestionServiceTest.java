package city.smart.ingestion.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyDouble;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

import city.smart.ingestion.dto.IngestionResponseDto;
import city.smart.ingestion.dto.SensorReadingDto;
import city.smart.ingestion.kafka.TrafficEventPublisher;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.jdbc.core.JdbcTemplate;

/** Unit tests for {@link IngestionService} with all infrastructure mocked. */
@ExtendWith(MockitoExtension.class)
class IngestionServiceTest {

  @Mock private JdbcTemplate jdbcTemplate;
  @Mock private SegmentLookupService segmentLookupService;
  @Mock private TrafficEventPublisher publisher;

  private IngestionService ingestionService;

  @BeforeEach
  void setUp() {
    ingestionService =
        new IngestionService(
            jdbcTemplate, segmentLookupService, publisher, new SimpleMeterRegistry());
  }

  @Test
  void ingestSingleReadingSuccess() {
    when(segmentLookupService.resolveSegment(anyString(), anyDouble(), anyDouble()))
        .thenReturn("seg-001");
    when(jdbcTemplate.update(anyString(), any(), any(), any(), any(), any(), any()))
        .thenReturn(1);

    IngestionResponseDto resp = ingestionService.ingest(List.of(sampleDto("s1")), "rest");

    assertThat(resp.getAccepted()).isEqualTo(1);
    assertThat(resp.getRejected()).isEqualTo(0);
    assertThat(resp.getRoadSegmentId()).isEqualTo("seg-001");
  }

  @Test
  void ingestCountsRejectedOnDbError() {
    when(segmentLookupService.resolveSegment(anyString(), anyDouble(), anyDouble()))
        .thenReturn("seg-001");
    when(jdbcTemplate.update(anyString(), any(), any(), any(), any(), any(), any()))
        .thenThrow(new RuntimeException("DB error"));

    IngestionResponseDto resp = ingestionService.ingest(List.of(sampleDto("s1")), "rest");

    assertThat(resp.getRejected()).isEqualTo(1);
    assertThat(resp.getAccepted()).isEqualTo(0);
  }

  @Test
  void ingestBatchPartialSuccess() {
    when(segmentLookupService.resolveSegment(anyString(), anyDouble(), anyDouble()))
        .thenReturn("seg-001");
    // first call succeeds, second throws
    when(jdbcTemplate.update(anyString(), any(), any(), any(), any(), any(), any()))
        .thenReturn(1)
        .thenThrow(new RuntimeException("constraint violation"));

    IngestionResponseDto resp =
        ingestionService.ingest(List.of(sampleDto("s1"), sampleDto("s2")), "mqtt");

    assertThat(resp.getAccepted()).isEqualTo(1);
    assertThat(resp.getRejected()).isEqualTo(1);
  }

  private SensorReadingDto sampleDto(String sensorId) {
    SensorReadingDto dto = new SensorReadingDto();
    dto.setSensorId(sensorId);
    dto.setTs(1_700_000_000L);
    dto.setLat(31.7);
    dto.setLon(35.2);
    dto.setVehicleCount(5);
    dto.setAvgSpeedKmh(40.0);
    dto.setOccupancyPct(20.0);
    return dto;
  }
}
