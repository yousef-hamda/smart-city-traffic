"""Feast feature definitions for traffic prediction."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from feast import Entity, FeatureView, Field  # type: ignore[import-untyped]
from feast.types import Float32, Int64  # type: ignore[import-untyped]
from feast import FileSource  # type: ignore[import-untyped]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARQUET_PATH = str(_REPO_ROOT / "ml" / "data" / "training.parquet")

# Entity
segment = Entity(
    name="segment_id",
    description="Road segment identifier",
)

# Source
traffic_source = FileSource(
    path=_PARQUET_PATH,
    timestamp_field="event_timestamp",
)

# Feature view
traffic_features_view = FeatureView(
    name="traffic_features",
    entities=[segment],
    ttl=timedelta(hours=48),
    schema=[
        Field(name="vehicle_count", dtype=Float32),
        Field(name="avg_speed_kmh", dtype=Float32),
        Field(name="occupancy_pct", dtype=Float32),
        Field(name="hour", dtype=Int64),
        Field(name="day_of_week", dtype=Int64),
        Field(name="is_weekend", dtype=Int64),
        Field(name="is_rush", dtype=Int64),
        Field(name="lag_1h", dtype=Float32),
        Field(name="lag_24h", dtype=Float32),
        Field(name="rolling_mean_3h", dtype=Float32),
    ],
    source=traffic_source,
    description="Engineered traffic features per road segment",
)
