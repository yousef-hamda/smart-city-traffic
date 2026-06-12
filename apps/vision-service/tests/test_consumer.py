import base64

import cv2
from _frames import CAR_BGR, make_frame

from vision_service.config import Settings
from vision_service.consumer import VisionConsumer
from vision_service.snapshots import SnapshotStore


def _envelope(camera_id: str, segment_id: str, seq: int, x: int) -> dict[str, object]:
    frame = make_frame([(x, 300, 70, 40, CAR_BGR)])
    ok, buf = cv2.imencode(".jpg", frame)
    assert ok
    return {
        "camera_id": camera_id,
        "segment_id": segment_id,
        "seq": seq,
        "ts": "2026-06-08T08:00:00+03:00",
        "image_b64": base64.b64encode(buf.tobytes()).decode("ascii"),
    }


def test_handle_envelope_populates_snapshot_and_event() -> None:
    store = SnapshotStore()
    consumer = VisionConsumer(Settings(detector="synthetic"), store)

    event = None
    x = 200
    for seq in range(4):
        event = consumer.handle_envelope(_envelope("C-jaffa-road-00", "jaffa-road-00", seq, x))
        x += 30

    assert consumer.processed == 4
    assert event is not None and event.segment_id == "jaffa-road-00"
    png = store.get("jaffa-road-00")
    assert png is not None and png[:8] == b"\x89PNG\r\n\x1a\n"
    assert "jaffa-road-00" in store.segments()


def test_pipeline_persists_per_camera_identity() -> None:
    store = SnapshotStore()
    consumer = VisionConsumer(Settings(detector="synthetic"), store)
    consumer.handle_envelope(_envelope("C-a", "seg-a", 0, 200))
    consumer.handle_envelope(_envelope("C-b", "seg-b", 0, 200))
    # Two cameras → two independent pipelines/trackers.
    assert len(consumer._pipelines) == 2  # noqa: SLF001 - whitebox check
