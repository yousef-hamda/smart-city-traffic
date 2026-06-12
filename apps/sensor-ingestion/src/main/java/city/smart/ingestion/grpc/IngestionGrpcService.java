package city.smart.ingestion.grpc;

import city.smart.ingestion.dto.IngestionResponseDto;
import city.smart.ingestion.dto.SensorReadingDto;
import city.smart.ingestion.service.IngestionService;
import city.smart.proto.traffic.v1.IngestionServiceGrpc;
import city.smart.proto.traffic.v1.PublishAck;
import city.smart.proto.traffic.v1.SensorReading;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.SmartLifecycle;
import org.springframework.stereotype.Component;

/**
 * gRPC server implementing the {@code IngestionService} contract defined in
 * {@code ingestion.proto}. Manages its own lifecycle via {@link SmartLifecycle} so it starts after
 * the Spring context is fully wired and shuts down cleanly before the context closes.
 */
@Component
public class IngestionGrpcService extends IngestionServiceGrpc.IngestionServiceImplBase
    implements SmartLifecycle {

  private static final Logger log = LoggerFactory.getLogger(IngestionGrpcService.class);

  private final IngestionService ingestionService;
  private final int grpcPort;

  private io.grpc.Server grpcServer;
  private volatile boolean running = false;

  public IngestionGrpcService(
      IngestionService ingestionService, @Value("${grpc.port:9091}") int grpcPort) {
    this.ingestionService = ingestionService;
    this.grpcPort = grpcPort;
  }

  @Override
  public void start() {
    try {
      grpcServer = ServerBuilder.forPort(grpcPort).addService(this).build().start();
      running = true;
      int actualPort = grpcServer.getPort();
      log.info("gRPC server started on port {}", actualPort);
    } catch (IOException e) {
      log.error("Failed to start gRPC server on port {}: {}", grpcPort, e.getMessage(), e);
    }
  }

  @Override
  public void stop() {
    running = false;
    if (grpcServer != null) {
      grpcServer.shutdown();
      try {
        grpcServer.awaitTermination(10, TimeUnit.SECONDS);
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        grpcServer.shutdownNow();
      }
    }
  }

  @Override
  public boolean isRunning() {
    return running;
  }

  @Override
  public void publishReading(
      SensorReading request, StreamObserver<PublishAck> responseObserver) {
    IngestionResponseDto resp = ingestionService.ingest(List.of(toDto(request)), "grpc");
    responseObserver.onNext(toAck(resp));
    responseObserver.onCompleted();
  }

  @Override
  public StreamObserver<SensorReading> publishReadings(
      StreamObserver<PublishAck> responseObserver) {
    List<SensorReadingDto> buffer = new ArrayList<>();
    return new StreamObserver<SensorReading>() {
      @Override
      public void onNext(SensorReading value) {
        buffer.add(toDto(value));
      }

      @Override
      public void onError(Throwable t) {
        log.warn("gRPC publishReadings stream error: {}", t.getMessage());
        responseObserver.onError(t);
      }

      @Override
      public void onCompleted() {
        IngestionResponseDto resp = ingestionService.ingest(buffer, "grpc");
        responseObserver.onNext(toAck(resp));
        responseObserver.onCompleted();
      }
    };
  }

  private SensorReadingDto toDto(SensorReading r) {
    SensorReadingDto dto = new SensorReadingDto();
    dto.setSensorId(r.getSensorId());
    dto.setTs(r.getTs().getSeconds());
    dto.setLat(r.getLat());
    dto.setLon(r.getLon());
    dto.setVehicleCount((int) r.getVehicleCount());
    dto.setAvgSpeedKmh(r.getAvgSpeedKmh());
    dto.setOccupancyPct(r.getOccupancyPct());
    return dto;
  }

  private PublishAck toAck(IngestionResponseDto resp) {
    return PublishAck.newBuilder()
        .setAccepted(resp.getAccepted())
        .setRejected(resp.getRejected())
        .setRoadSegmentId(resp.getRoadSegmentId() != null ? resp.getRoadSegmentId() : "")
        .build();
  }
}
