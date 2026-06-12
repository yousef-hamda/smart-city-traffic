// Live edge-weight update, applied by the realtime gateway as fresh segment
// speeds arrive. Travel time = length / speed; the dashboard's route advice
// and centrality then reflect current congestion rather than free-flow.
//
// Parameters: $updates = [{segment_id, speed_kmh}, ...]

UNWIND $updates AS u
MATCH (s:RoadSegment {id: u.segment_id})-[r:CONNECTS_TO]->(:RoadSegment)
SET r.current_time_s =
  CASE WHEN u.speed_kmh > 0
       THEN r.length_m / (u.speed_kmh / 3.6)
       ELSE r.freeflow_time_s * 5  // treat ~stopped as heavily penalised
  END
RETURN count(r) AS edges_updated;
