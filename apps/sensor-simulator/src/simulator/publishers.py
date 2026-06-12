"""Publishing backends: MQTT (device-style), HTTP bulk (gateway-style), stdout.

The simulator mirrors a real ITS deployment: most readings arrive as MQTT
device messages; the HTTP path exercises the ingestion service's public bulk
endpoint. Stdout is the default so the CLI works with no infrastructure.
"""

import json
import sys
from collections.abc import Sequence
from types import TracebackType
from typing import Protocol

import httpx
import structlog

from simulator.model import Reading

logger = structlog.get_logger()


class Publisher(Protocol):
    def publish(self, readings: Sequence[Reading]) -> None: ...

    def close(self) -> None: ...


class StdoutPublisher:
    """Writes NDJSON to stdout — useful for piping and for dry runs."""

    def publish(self, readings: Sequence[Reading]) -> None:
        for reading in readings:
            sys.stdout.write(json.dumps(reading.as_dict(), ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def close(self) -> None:  # pragma: no cover - nothing to release
        return None


class MqttPublisher:
    """Publishes each reading to ``sensors/{sensor_id}/readings`` (QoS 1)."""

    def __init__(self, host: str, port: int = 1883) -> None:
        # Imported lazily so stdout/http runs don't require paho.
        import paho.mqtt.client as mqtt
        from paho.mqtt.enums import CallbackAPIVersion

        self._client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id="sensor-simulator",
        )
        self._client.connect(host, port)
        self._client.loop_start()

    def publish(self, readings: Sequence[Reading]) -> None:
        for reading in readings:
            self._client.publish(
                f"sensors/{reading.sensor_id}/readings",
                json.dumps(reading.as_dict(), ensure_ascii=False),
                qos=1,
            )

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()


class HttpPublisher:
    """POSTs batches to the ingestion service's bulk endpoint."""

    def __init__(self, base_url: str, timeout_s: float = 10.0) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_s)

    def publish(self, readings: Sequence[Reading]) -> None:
        if not readings:
            return
        response = self._client.post(
            "/api/v1/readings/bulk",
            json=[r.as_dict() for r in readings],
        )
        if response.status_code >= 400:
            logger.warning(
                "http_publish_rejected",
                status=response.status_code,
                body=response.text[:500],
            )

    def close(self) -> None:
        self._client.close()


class CompositePublisher:
    """Fans a batch out to several backends, closing all of them on exit."""

    def __init__(self, publishers: Sequence[Publisher]) -> None:
        self._publishers = list(publishers)

    def publish(self, readings: Sequence[Reading]) -> None:
        for publisher in self._publishers:
            publisher.publish(readings)

    def close(self) -> None:
        for publisher in self._publishers:
            publisher.close()

    def __enter__(self) -> "CompositePublisher":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
