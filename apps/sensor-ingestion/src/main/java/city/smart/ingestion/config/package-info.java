/**
 * Configuration classes for the sensor-ingestion service.
 *
 * <p>The service follows a layered architecture that Phase 2 fills in:
 *
 * <ul>
 *   <li>{@code city.smart.ingestion.api} &mdash; REST controllers and (Phase 2) gRPC endpoints.
 *       Thin transport layer; validation and DTO mapping only.
 *   <li>{@code city.smart.ingestion.service} &mdash; (Phase 2) business logic: sensor payload
 *       normalization, PostGIS geo-enrichment, deduplication and Kafka publishing.
 *   <li>{@code city.smart.ingestion.repository} &mdash; (Phase 2) data access: JPA/PostGIS
 *       repositories for sensor metadata and road-segment geometry.
 * </ul>
 *
 * <p>Phase 2 configuration expected here: MQTT client (Paho), Kafka producer, gRPC server,
 * Resilience4j policies and datasource tuning.
 */
package city.smart.ingestion.config;
