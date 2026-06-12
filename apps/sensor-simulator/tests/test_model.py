import random
from datetime import datetime
from zoneinfo import ZoneInfo

from simulator.model import Hotspot, TrafficModel, demand_factor
from simulator.network import Sensor

TZ = ZoneInfo("Asia/Jerusalem")

SENSOR = Sensor(id="S-test-1", segment_id="test-00", lat=31.78, lon=35.21)


def _avg_speed(model: TrafficModel, at: datetime, runs: int = 50) -> float:
    readings = [
        model.reading(SENSOR, speed_limit_kmh=50, at=at, interval_s=5.0) for _ in range(runs)
    ]
    return sum(r.avg_speed_kmh for r in readings) / runs


def test_weekday_rush_hour_exceeds_night_demand() -> None:
    rush = datetime(2026, 6, 8, 8, 0, tzinfo=TZ)  # Monday 08:00
    night = datetime(2026, 6, 8, 3, 0, tzinfo=TZ)
    assert demand_factor(rush) > 4 * demand_factor(night)


def test_saturday_quieter_than_weekday_morning() -> None:
    weekday = datetime(2026, 6, 8, 8, 0, tzinfo=TZ)  # Monday
    saturday = datetime(2026, 6, 13, 8, 0, tzinfo=TZ)
    assert demand_factor(saturday) < 0.4 * demand_factor(weekday)


def test_friday_peaks_before_shabbat_not_evening() -> None:
    late_morning = datetime(2026, 6, 12, 11, 0, tzinfo=TZ)  # Friday
    evening = datetime(2026, 6, 12, 19, 0, tzinfo=TZ)
    assert demand_factor(late_morning) > 2 * demand_factor(evening)


def test_rush_hour_slows_traffic() -> None:
    model = TrafficModel(rng=random.Random(7))
    rush = datetime(2026, 6, 8, 8, 0, tzinfo=TZ)
    night = datetime(2026, 6, 8, 3, 0, tzinfo=TZ)
    assert _avg_speed(model, rush) < _avg_speed(model, night) - 5


def test_incident_capacity_factor_degrades_flow() -> None:
    model = TrafficModel(rng=random.Random(7))
    at = datetime(2026, 6, 8, 8, 0, tzinfo=TZ)
    normal = [
        model.reading(SENSOR, 50, at, 5.0, capacity_factor=1.0).avg_speed_kmh
        for _ in range(50)
    ]
    incident = [
        model.reading(SENSOR, 50, at, 5.0, capacity_factor=0.35).avg_speed_kmh
        for _ in range(50)
    ]
    assert sum(incident) / 50 < sum(normal) / 50 - 5


def test_hotspot_raises_local_demand() -> None:
    on_hotspot = TrafficModel(
        hotspots=[Hotspot("test", SENSOR.lat, SENSOR.lon, weight=0.8, radius_m=600)],
        rng=random.Random(7),
    )
    assert on_hotspot.hotspot_multiplier(SENSOR) > 1.7


def test_reading_payload_matches_contract() -> None:
    model = TrafficModel(rng=random.Random(7))
    reading = model.reading(SENSOR, 50, datetime(2026, 6, 8, 8, 0, tzinfo=TZ), 5.0)
    payload = reading.as_dict()
    assert set(payload) == {
        "sensor_id", "ts", "lat", "lon", "vehicle_count", "avg_speed_kmh", "occupancy_pct",
    }
    assert 0 <= float(payload["occupancy_pct"]) <= 100  # type: ignore[arg-type]
    assert float(payload["avg_speed_kmh"]) >= 4.0  # type: ignore[arg-type]
