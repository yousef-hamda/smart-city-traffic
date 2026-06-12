// Uniqueness constraints (also create backing indexes). Idempotent.
// Applied automatically by scripts/seed/seed_neo4j.py; kept here for ops use.

CREATE CONSTRAINT segment_id IF NOT EXISTS
FOR (s:RoadSegment) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT neighborhood_id IF NOT EXISTS
FOR (n:Neighborhood) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT sensor_id IF NOT EXISTS
FOR (s:Sensor) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT intersection_id IF NOT EXISTS
FOR (i:Intersection) REQUIRE i.id IS UNIQUE;
