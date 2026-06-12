// Reachability under an incident: which segments lose connectivity from a
// chosen origin if segment $closed is shut.
//
// Compares the set of segments reachable from $origin before and after
// removing $closed. Segments in (before \ after) are cut off by the closure —
// the blast radius of an incident or planned roadworks. Parameters:
//   $origin  RoadSegment id to measure connectivity from
//   $closed  RoadSegment id taken out of service
//
// Requires APOC (bundled in the docker-compose neo4j image).

MATCH (origin:RoadSegment {id: $origin})
MATCH (closed:RoadSegment {id: $closed})

CALL apoc.path.subgraphNodes(origin, {
  relationshipFilter: 'CONNECTS_TO>',
  labelFilter: '+RoadSegment'
}) YIELD node AS before
WITH origin, closed, collect(before.id) AS reachable_before

CALL apoc.path.subgraphNodes(origin, {
  relationshipFilter: 'CONNECTS_TO>',
  labelFilter: '+RoadSegment',
  blacklistNodes: [closed]
}) YIELD node AS after
WITH closed, reachable_before, collect(after.id) AS reachable_after

RETURN
  closed.id AS closed_segment,
  [s IN reachable_before WHERE NOT s IN reachable_after] AS lost_segments,
  size(reachable_before) AS reachable_before_count,
  size(reachable_after) AS reachable_after_count;
