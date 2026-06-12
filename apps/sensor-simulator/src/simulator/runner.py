"""Tick loop: generate one reading per sensor per interval and publish."""

import time
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import structlog

from simulator.incidents import IncidentManager
from simulator.model import Reading, TrafficModel
from simulator.network import Network
from simulator.publishers import Publisher

logger = structlog.get_logger()

JERUSALEM_TZ = ZoneInfo("Asia/Jerusalem")


@dataclass
class SimulationRunner:
    network: Network
    model: TrafficModel
    incidents: IncidentManager
    publisher: Publisher
    interval_s: float

    def tick(self, at: datetime) -> list[Reading]:
        """Produce one network-wide batch for the window ending at ``at``."""
        self.incidents.prune(at)
        injected = self.incidents.maybe_inject_random(at, self.interval_s)
        if injected is not None:
            logger.info(
                "incident_started",
                segment_id=injected.segment_id,
                ends_at=injected.ends_at.isoformat(),
            )

        segment_by_id = {segment.id: segment for segment in self.network.segments}
        readings = [
            self.model.reading(
                sensor,
                speed_limit_kmh=segment_by_id[sensor.segment_id].speed_limit_kmh,
                at=at,
                interval_s=self.interval_s,
                capacity_factor=self.incidents.capacity_factor(sensor.segment_id, at),
            )
            for sensor in self.network.sensors
        ]
        self.publisher.publish(readings)
        return readings

    def run(self, duration_s: float | None = None) -> int:
        """Loop until interrupted (or for ``duration_s``); returns batches sent."""
        batches = 0
        started = time.monotonic()
        logger.info(
            "simulation_started",
            sensors=len(self.network.sensors),
            interval_s=self.interval_s,
        )
        try:
            while True:
                tick_started = time.monotonic()
                self.tick(datetime.now(tz=JERUSALEM_TZ))
                batches += 1
                if duration_s is not None and time.monotonic() - started >= duration_s:
                    break
                elapsed = time.monotonic() - tick_started
                time.sleep(max(0.0, self.interval_s - elapsed))
        except KeyboardInterrupt:  # pragma: no cover - interactive only
            logger.info("simulation_interrupted")
        logger.info("simulation_finished", batches=batches)
        return batches
