package city.smart.ingestion.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

/** DTO for a single sensor reading submitted via REST, MQTT, or gRPC. */
public class SensorReadingDto {

  @NotBlank
  private String sensorId;

  /** Unix epoch seconds. */
  private long ts;

  @DecimalMin("-90.0")
  @DecimalMax("90.0")
  private double lat;

  @DecimalMin("-180.0")
  @DecimalMax("180.0")
  private double lon;

  @Min(0)
  private int vehicleCount;

  @DecimalMin("0.0")
  private double avgSpeedKmh;

  @DecimalMin("0.0")
  @DecimalMax("100.0")
  private double occupancyPct;

  public String getSensorId() {
    return sensorId;
  }

  public void setSensorId(String sensorId) {
    this.sensorId = sensorId;
  }

  public long getTs() {
    return ts;
  }

  public void setTs(long ts) {
    this.ts = ts;
  }

  public double getLat() {
    return lat;
  }

  public void setLat(double lat) {
    this.lat = lat;
  }

  public double getLon() {
    return lon;
  }

  public void setLon(double lon) {
    this.lon = lon;
  }

  public int getVehicleCount() {
    return vehicleCount;
  }

  public void setVehicleCount(int vehicleCount) {
    this.vehicleCount = vehicleCount;
  }

  public double getAvgSpeedKmh() {
    return avgSpeedKmh;
  }

  public void setAvgSpeedKmh(double avgSpeedKmh) {
    this.avgSpeedKmh = avgSpeedKmh;
  }

  public double getOccupancyPct() {
    return occupancyPct;
  }

  public void setOccupancyPct(double occupancyPct) {
    this.occupancyPct = occupancyPct;
  }
}
