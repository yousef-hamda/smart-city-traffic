package city.smart.ingestion.dto;

/** Response payload returned from ingestion endpoints. */
public class IngestionResponseDto {

  private long accepted;
  private long rejected;
  /** Road segment resolved via PostGIS lookup for the last accepted reading. */
  private String roadSegmentId;

  public IngestionResponseDto(long accepted, long rejected, String roadSegmentId) {
    this.accepted = accepted;
    this.rejected = rejected;
    this.roadSegmentId = roadSegmentId;
  }

  public long getAccepted() {
    return accepted;
  }

  public long getRejected() {
    return rejected;
  }

  public String getRoadSegmentId() {
    return roadSegmentId;
  }
}
