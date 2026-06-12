// Betweenness centrality: which segments carry the most shortest-path flow.
//
// High betweenness = a segment many fastest routes pass through, i.e. a
// network choke point whose closure or congestion hurts most. The dashboard
// and the AI assistant use this to rank "segments that matter most to flow".

CALL gds.graph.project(
  'roadnet_centrality',
  'RoadSegment',
  { CONNECTS_TO: { properties: 'current_time_s' } }
) YIELD graphName;

CALL gds.betweenness.stream('roadnet_centrality', {
  relationshipWeightProperty: 'current_time_s'
})
YIELD nodeId, score
RETURN
  gds.util.asNode(nodeId).id AS segment_id,
  gds.util.asNode(nodeId).name_en AS name_en,
  score AS betweenness
ORDER BY betweenness DESC
LIMIT 20;

// CALL gds.graph.drop('roadnet_centrality') YIELD graphName;
