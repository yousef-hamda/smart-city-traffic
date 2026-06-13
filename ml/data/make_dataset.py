"""Generate synthetic historical traffic dataset for model training.

Imports the sensor simulator's demand model by adding apps/sensor-simulator/src
to sys.path so we can reuse demand_factor() and the network geometry.
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add simulator to path before importing it
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "apps" / "sensor-simulator" / "src"))

import numpy as np
import pandas as pd

from simulator.model import TrafficModel  # type: ignore[import-untyped]
from simulator.network import load_network  # type: ignore[import-untyped]

SEED = 42
MAX_ROWS = 3000
DAYS = 60
OUTPUT_DIR = Path(__file__).resolve().parent


def main() -> None:
    rng = random.Random(SEED)
    np_rng = np.random.default_rng(SEED)

    network_path = _REPO_ROOT / "scripts" / "seed" / "data" / "jerusalem_roads.json"
    network = load_network(network_path)

    model = TrafficModel(rng=random.Random(SEED))

    start_dt = datetime(2024, 1, 1, 0, 0, 0)
    records: list[dict[str, object]] = []

    # Sample subset of segments to keep dataset small
    segments = list(network.segments)
    rng.shuffle(segments)

    rows_per_segment = MAX_ROWS // max(len(segments), 1)
    hours_total = DAYS * 24

    for segment in segments:
        sensors = network.sensors_for_segment(segment.id)
        if not sensors:
            continue
        sensor = sensors[0]

        # Pick evenly-spaced hours across the 60-day window
        step = max(1, hours_total // max(rows_per_segment, 1))
        hour_indices = list(range(0, hours_total, step))[:rows_per_segment]

        for h in hour_indices:
            at = start_dt + timedelta(hours=h)
            reading = model.reading(
                sensor=sensor,
                speed_limit_kmh=segment.speed_limit_kmh,
                at=at,
                interval_s=3600.0,
            )
            records.append(
                {
                    "segment_id": segment.id,
                    "ts": at,
                    "vehicle_count": reading.vehicle_count,
                    "avg_speed_kmh": reading.avg_speed_kmh,
                    "occupancy_pct": reading.occupancy_pct,
                    "speed_limit_kmh": segment.speed_limit_kmh,
                }
            )

        if len(records) >= MAX_ROWS:
            break

    df = pd.DataFrame(records[:MAX_ROWS])
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.sort_values(["segment_id", "ts"]).reset_index(drop=True)

    # Engineer time features
    df["hour"] = df["ts"].dt.hour
    df["day_of_week"] = df["ts"].dt.dayofweek  # 0=Mon in pandas but consistent
    df["is_weekend"] = df["day_of_week"].isin([4, 5]).astype(int)  # Fri=4, Sat=5 in Israeli week context
    df["is_rush"] = df["hour"].isin([7, 8, 9, 16, 17, 18]).astype(int)

    # Lag features per segment
    df["lag_1h"] = df.groupby("segment_id")["vehicle_count"].shift(1)
    df["lag_24h"] = df.groupby("segment_id")["vehicle_count"].shift(24)
    df["rolling_mean_3h"] = (
        df.groupby("segment_id")["vehicle_count"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    # Fill NaN lags with column mean
    for col in ["lag_1h", "lag_24h"]:
        df[col] = df[col].fillna(df["vehicle_count"].mean())

    # Add event_time for Feast compatibility
    df["event_timestamp"] = df["ts"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "training.csv"
    parquet_path = OUTPUT_DIR / "training.parquet"

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"Saved {len(df)} rows to {csv_path}")
    print(f"Saved parquet to {parquet_path}")
    print(f"Columns: {list(df.columns)}")
    print(f"Segments: {df['segment_id'].nunique()}")


if __name__ == "__main__":
    main()
