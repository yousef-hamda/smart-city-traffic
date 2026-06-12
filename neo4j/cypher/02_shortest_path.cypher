// Live-weighted shortest path between two segments.
//
// CONNECTS_TO.current_time_s is the travel time the realtime gateway keeps
// fresh from live speeds (it falls back to freeflow_time_s at seed time), so
// this returns the fastest route given *current* congestion. Parameters:
//   $source, $target  RoadSegment ids
//
// Uses GDS Dijkstra. Requires the Graph Data Science plugin (bundled in the
// docker-compose neo4j image via NEO4J_PLUGINS).

// 1) Project a weighted graph from the live travel times.
CALL gds.graph.project(
  'roadnet',
  'RoadSegment',
  { CONNECTS_TO: { properties: 'current_time_s' } }
) YIELD graphName;

// 2) Source-target Dijkstra over current_time_s.
MATCH (src:RoadSegment {id: $source}), (dst:RoadSegment {id: $target})
CALL gds.shortestPath.dijkstra.stream('roadnet', {
  sourceNode: src,
  targetNode: dst,
  relationshipWeightProperty: 'current_time_s'
})
YIELD totalCost, nodeIds, costs
RETURN
  totalCost AS total_seconds,
  [nodeId IN nodeIds | gds.util.asNode(nodeId).id] AS segment_path,
  costs;

// 3) Release the projection (call after consuming results).
// CALL gds.graph.drop('roadnet') YIELD graphName;
