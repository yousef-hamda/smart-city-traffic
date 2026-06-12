from pathlib import Path

import pytest

from simulator.model import Reading
from simulator.publishers import Publisher
from simulator.replay import load_scenario, replay


class _Capture:
    def __init__(self) -> None:
        self.readings: list[Reading] = []

    def publish(self, readings: list[Reading]) -> None:  # type: ignore[override]
        self.readings.extend(readings)

    def close(self) -> None:
        return None


_publisher: Publisher = _Capture()  # protocol conformance check


def _write_scenario(path: Path, body: str) -> Path:
    path.write_text(
        "offset_s,sensor_id,lat,lon,vehicle_count,avg_speed_kmh,occupancy_pct\n" + body,
        encoding="utf-8",
    )
    return path


def test_replay_publishes_rows_in_offset_order(tmp_path: Path) -> None:
    scenario = _write_scenario(
        tmp_path / "s.csv",
        "0.02,S-b,31.78,35.21,5,40.0,12.0\n0.0,S-a,31.78,35.21,9,30.0,20.0\n",
    )
    capture = _Capture()
    count = replay(scenario, capture, speedup=100.0)
    assert count == 2
    assert [r.sensor_id for r in capture.readings] == ["S-a", "S-b"]


def test_missing_columns_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("offset_s,sensor_id\n0,S-a\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        load_scenario(bad)


def test_malformed_row_reports_line_number(tmp_path: Path) -> None:
    scenario = _write_scenario(tmp_path / "s.csv", "not-a-number,S-a,31.78,35.21,5,40.0,12.0\n")
    with pytest.raises(ValueError, match="line 2"):
        load_scenario(scenario)
