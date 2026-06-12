package city.smart.ingestion.service;

import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/**
 * Resolves the nearest road segment for a given sensor location using PostGIS nearest-neighbour
 * search. Results are cached in-memory by sensor ID since sensor positions do not move.
 */
@Service
public class SegmentLookupService {

  private static final Logger log = LoggerFactory.getLogger(SegmentLookupService.class);

  private final JdbcTemplate jdbc;
  private final ConcurrentHashMap<String, String> cache = new ConcurrentHashMap<>();

  public SegmentLookupService(JdbcTemplate jdbc) {
    this.jdbc = jdbc;
  }

  /**
   * Returns the road segment ID nearest to the given coordinates. Returns an empty string when no
   * segment can be resolved (e.g. PostGIS unavailable or no segments seeded).
   */
  public String resolveSegment(String sensorId, double lat, double lon) {
    return cache.computeIfAbsent(sensorId, id -> lookupNearest(lat, lon));
  }

  private String lookupNearest(double lat, double lon) {
    try {
      return jdbc.queryForObject(
          "SELECT id FROM road_segments"
              + " ORDER BY geometry <-> ST_SetSRID(ST_MakePoint(?,?),4326) LIMIT 1",
          String.class,
          lon,
          lat);
    } catch (Exception e) {
      log.debug("Segment lookup failed for ({},{}): {}", lat, lon, e.getMessage());
      return "";
    }
  }
}
