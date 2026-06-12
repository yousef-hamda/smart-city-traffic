package city.smart.ingestion.mqtt;

import city.smart.ingestion.dto.SensorReadingDto;
import city.smart.ingestion.service.IngestionService;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.SmartLifecycle;
import org.springframework.stereotype.Component;

/**
 * Subscribes to an MQTT broker and forwards arriving sensor payloads into the ingestion pipeline.
 * Only created when {@code ingestion.mqtt.enabled=true} (the default).
 *
 * <p>Connection failures are retried up to three times with a 5-second back-off; after that the
 * service continues without MQTT rather than preventing startup.
 */
@Component
@ConditionalOnProperty(
    name = "ingestion.mqtt.enabled",
    havingValue = "true",
    matchIfMissing = true)
public class MqttReadingSubscriber implements SmartLifecycle, MqttCallback {

  private static final Logger log = LoggerFactory.getLogger(MqttReadingSubscriber.class);

  private final String brokerUrl;
  private final String clientId;
  private final String topic;
  private final IngestionService ingestionService;
  private final ObjectMapper objectMapper;

  private volatile MqttClient client;
  private volatile boolean running = false;

  public MqttReadingSubscriber(
      @Value("${ingestion.mqtt.broker-url}") String brokerUrl,
      @Value("${ingestion.mqtt.client-id}") String clientId,
      @Value("${ingestion.mqtt.topic}") String topic,
      IngestionService ingestionService,
      ObjectMapper objectMapper) {
    this.brokerUrl = brokerUrl;
    this.clientId = clientId;
    this.topic = topic;
    this.ingestionService = ingestionService;
    this.objectMapper = objectMapper;
  }

  @Override
  public void start() {
    running = true;
    Thread.ofVirtual().name("mqtt-connect").start(this::connectWithRetry);
  }

  private void connectWithRetry() {
    int attempts = 0;
    while (running && attempts < 3) {
      try {
        client = new MqttClient(brokerUrl, clientId, new MemoryPersistence());
        client.setCallback(this);
        MqttConnectOptions opts = new MqttConnectOptions();
        opts.setCleanSession(true);
        opts.setAutomaticReconnect(true);
        client.connect(opts);
        client.subscribe(topic, 1);
        log.info("MQTT connected to {} and subscribed to {}", brokerUrl, topic);
        return;
      } catch (Exception e) {
        attempts++;
        log.warn("MQTT connect attempt {}/3 failed: {}", attempts, e.getMessage());
        try {
          Thread.sleep(5_000);
        } catch (InterruptedException ie) {
          Thread.currentThread().interrupt();
          return;
        }
      }
    }
    log.warn(
        "MQTT connection failed after 3 attempts — broker unavailable, continuing without MQTT");
  }

  @Override
  public void stop() {
    running = false;
    if (client != null && client.isConnected()) {
      try {
        client.disconnect();
      } catch (MqttException e) {
        log.warn("Error disconnecting MQTT: {}", e.getMessage());
      }
    }
  }

  @Override
  public boolean isRunning() {
    return running;
  }

  @Override
  public void connectionLost(Throwable cause) {
    log.warn("MQTT connection lost: {}", cause.getMessage());
  }

  @Override
  public void messageArrived(String incomingTopic, MqttMessage message) {
    try {
      SensorReadingDto dto =
          objectMapper.readValue(message.getPayload(), SensorReadingDto.class);
      ingestionService.ingest(List.of(dto), "mqtt");
    } catch (Exception e) {
      log.warn(
          "Failed to process MQTT message on topic {}: {}", incomingTopic, e.getMessage());
    }
  }

  @Override
  public void deliveryComplete(IMqttDeliveryToken token) {
    // Not used — this service only subscribes.
  }
}
