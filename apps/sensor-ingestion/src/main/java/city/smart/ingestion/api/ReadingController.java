package city.smart.ingestion.api;

import city.smart.ingestion.dto.IngestionResponseDto;
import city.smart.ingestion.dto.SensorReadingDto;
import city.smart.ingestion.service.IngestionService;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/** REST endpoints for submitting sensor readings. */
@RestController
@RequestMapping("/api/v1/readings")
public class ReadingController {

  private final IngestionService ingestionService;

  public ReadingController(IngestionService ingestionService) {
    this.ingestionService = ingestionService;
  }

  /** Submit a single sensor reading. */
  @PostMapping
  @ResponseStatus(HttpStatus.ACCEPTED)
  public IngestionResponseDto single(@Valid @RequestBody SensorReadingDto reading) {
    return ingestionService.ingest(List.of(reading), "rest");
  }

  /** Submit multiple sensor readings in a single request. */
  @PostMapping("/bulk")
  @ResponseStatus(HttpStatus.ACCEPTED)
  public IngestionResponseDto bulk(
      @RequestBody List<@Valid SensorReadingDto> readings) {
    return ingestionService.ingest(readings, "rest");
  }
}
