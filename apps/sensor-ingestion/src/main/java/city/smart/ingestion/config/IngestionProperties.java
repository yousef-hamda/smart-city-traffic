package city.smart.ingestion.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** Typed configuration for the MQTT subscriber. */
@Component
@ConfigurationProperties(prefix = "ingestion.mqtt")
public class IngestionProperties {

  private boolean enabled = true;
  private String brokerUrl = "tcp://localhost:1883";
  private String clientId = "sensor-ingestion-service";
  private String topic = "sensors/+/readings";

  public boolean isEnabled() {
    return enabled;
  }

  public void setEnabled(boolean enabled) {
    this.enabled = enabled;
  }

  public String getBrokerUrl() {
    return brokerUrl;
  }

  public void setBrokerUrl(String brokerUrl) {
    this.brokerUrl = brokerUrl;
  }

  public String getClientId() {
    return clientId;
  }

  public void setClientId(String clientId) {
    this.clientId = clientId;
  }

  public String getTopic() {
    return topic;
  }

  public void setTopic(String topic) {
    this.topic = topic;
  }
}
