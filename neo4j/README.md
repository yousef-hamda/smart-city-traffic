# Road-Network Knowledge Graph (Neo4j)

A property graph of the Jerusalem road network used for routing, centrality,
and incident-impact analysis. The AI assistant's `recommend_route` and
`reachability_impact` tools (Phase 13) query it; the realtime gateway keeps
edge weights fresh from live speeds.

## Model

```
(:Neighborhood)
(:RoadSegment)-[:IN_NEIGHBORHOOD]->(:Neighborhood)
(:RoadSegment)-[:OBSERVED_BY]->(:Sensor)
(:RoadSegment)-[:MEETS_AT]->(:Intersection)
(:RoadSegment)-[:CONNECTS_TO {length_m, freeflow_time_s, current_time_s}]->(:RoadSegment)
(:Incident)   // created at runtime, not seeded
```

Two segments are `CONNECTS_TO`-linked when they share an endpoint: sequential
segments of one road, or segments of different roads meeting at an
`Intersection` (endpoints clustered within ~130 m). `current_time_s` is the
live travel time (seeded to free-flow, updated by the realtime gateway); all
weighted queries use it so routes reflect current congestion.

## Derivation is shared and tested

The graph is derived by [`scripts/seed/graph_model.py`](../scripts/seed/graph_model.py),
the same module that backs the reference algorithms (`shortest_path`,
`reachability_impact`) and their unit tests. This keeps the Cypher seed and the
Python fallbacks in lock-step. `seed_neo4j.py` turns the derived nodes/edges
into idempotent `MERGE` statements.

```bash
pip install -r scripts/seed/requirements.txt
python3 scripts/seed/seed_neo4j.py          # NEO4J_URI / NEO4J_PASSWORD env
PYTHONPATH=apps/sensor-simulator/src:scripts/seed \
  python -m pytest scripts/seed/tests -q     # graph + algorithm tests
```

## Cypher library (`cypher/`)

| File                                    | Purpose                                    | Plugin |
| --------------------------------------- | ------------------------------------------ | ------ |
| `01_constraints.cypher`                 | uniqueness constraints / indexes           | —      |
| `02_shortest_path.cypher`               | live-weighted Dijkstra `$source → $target` | GDS    |
| `03_centrality.cypher`                  | betweenness — choke-point ranking          | GDS    |
| `04_reachability_under_incident.cypher` | blast radius of closing `$closed`          | APOC   |
| `05_live_weight_update.cypher`          | realtime gateway weight refresh            | —      |

GDS and APOC ship in the compose `neo4j:5` image via `NEO4J_PLUGINS`.
