package city.smart.ingestion.kafka;

import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

/**
 * Publishes enriched traffic events to the {@code traffic.raw} Kafka topic. Protected by a
 * Resilience4j circuit breaker so that Kafka outages do not cascade into the ingestion path.
 */
@Service
public class TrafficEventPublisher {

  private static final Logger log = LoggerFactory.getLogger(TrafficEventPublisher.class);
  private static final String TOPIC = "traffic.raw";

  private final KafkaTemplate<String, String> kafkaTemplate;

  public TrafficEventPublisher(KafkaTemplate<String, String> kafkaTemplate) {
    this.kafkaTemplate = kafkaTemplate;
  }

  /** Sends {@code json} to the traffic.raw topic keyed by {@code key} (segment ID). */
  @CircuitBreaker(name = "kafka-producer", fallbackMethod = "publishFallback")
  public void publish(String key, String json) {
    kafkaTemplate.send(TOPIC, key, json);
  }

  @SuppressWarnings("unused")
  void publishFallback(String key, String json, Exception e) {
    log.warn(
        "kafka-producer circuit open, dropping event for segment={}: {}", key, e.getMessage());
  }
}
