"""Kafka consumer: vision.frames → pipeline → vision.events + snapshots.

Runs on a background thread started by the FastAPI lifespan. One
:class:`CameraPipeline` is created lazily per camera id so tracker identities
persist. The loop is resilient: a malformed frame is logged and skipped, never
fatal.
"""

import json
import threading
from typing import Any

import structlog

from vision_service.config import Settings
from vision_service.detection import build_detector
from vision_service.incidents import IncidentDetector
from vision_service.pipeline import (
    CameraPipeline,
    VisionEvent,
    annotate,
    decode_frame,
    encode_png,
)
from vision_service.snapshots import SnapshotStore

logger = structlog.get_logger()


class VisionConsumer:
    def __init__(self, settings: Settings, snapshots: SnapshotStore) -> None:
        self._settings = settings
        self._snapshots = snapshots
        self._pipelines: dict[str, CameraPipeline] = {}
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        # kafka-python-ng ships no type stubs; treat its clients as Any.
        self._consumer: Any = None
        self._producer: Any = None
        self.processed = 0

    def _pipeline_for(self, camera_id: str, segment_id: str) -> CameraPipeline:
        if camera_id not in self._pipelines:
            self._pipelines[camera_id] = CameraPipeline(
                camera_id=camera_id,
                segment_id=segment_id,
                detector=build_detector(
                    self._settings.detector,
                    self._settings.yolo_weights,
                    self._settings.yolo_confidence,
                ),
                incident_detector=IncidentDetector(
                    fps=self._settings.assumed_fps,
                    stopped_seconds=self._settings.stopped_seconds,
                ),
                fps=self._settings.assumed_fps,
            )
        return self._pipelines[camera_id]

    def handle_envelope(self, envelope: dict[str, object]) -> VisionEvent:
        """Process one decoded frame envelope; returns the emitted event.

        Factored out of the loop so tests can drive it without Kafka.
        """
        camera_id = str(envelope["camera_id"])
        segment_id = str(envelope["segment_id"])
        seq = int(str(envelope["seq"]))
        ts = str(envelope["ts"])

        frame = decode_frame(str(envelope["image_b64"]))
        pipeline = self._pipeline_for(camera_id, segment_id)
        event = pipeline.process(frame, seq=seq, ts=ts)

        self._snapshots.put(segment_id, seq, encode_png(annotate(frame, event)))
        self.processed += 1
        return event

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="vision-consumer", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def _run(self) -> None:  # pragma: no cover - requires a live broker
        try:
            from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import-untyped]
        except ImportError:
            logger.warning("kafka_client_missing", note="consumer disabled")
            return

        try:
            self._consumer = KafkaConsumer(
                self._settings.frames_topic,
                bootstrap_servers=self._settings.kafka_bootstrap_servers.split(","),
                group_id=self._settings.consumer_group,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="latest",
                consumer_timeout_ms=1000,
            )
            self._producer = KafkaProducer(
                bootstrap_servers=self._settings.kafka_bootstrap_servers.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
            )
        except Exception as exc:  # noqa: BLE001 - broker may be down at boot
            logger.warning("kafka_connect_failed", error=str(exc))
            return

        logger.info("vision_consumer_started", topic=self._settings.frames_topic)
        while not self._stop.is_set():
            for message in self._consumer:
                if self._stop.is_set():
                    break
                try:
                    event = self.handle_envelope(message.value)
                    self._producer.send(
                        self._settings.events_topic,
                        key=event.segment_id,
                        value=event.to_envelope(),
                    )
                except Exception as exc:  # noqa: BLE001 - one bad frame must not kill the loop
                    logger.warning("frame_processing_failed", error=str(exc))
