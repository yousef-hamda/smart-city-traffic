import base64

import cv2
from _frames import CAR_BGR, make_frame

from vision_service.detection import SyntheticDetector
from vision_service.incidents import IncidentDetector
from vision_service.pipeline import CameraPipeline, annotate, decode_frame, encode_png
from vision_service.tracking import ByteTrackConfig, ByteTracker


def _pipeline() -> CameraPipeline:
    return CameraPipeline(
        camera_id="C-jaffa-road-00",
        segment_id="jaffa-road-00",
        detector=SyntheticDetector(),
        incident_detector=IncidentDetector(fps=15.0),
        fps=15.0,
        tracker=ByteTracker(ByteTrackConfig(min_hits=2)),
    )


def test_pipeline_tracks_and_counts_a_moving_car() -> None:
    pipeline = _pipeline()
    event = None
    x = 200
    for seq in range(5):
        frame = make_frame([(x, 300, 70, 40, CAR_BGR)])
        event = pipeline.process(frame, seq=seq, ts="2026-06-08T08:00:00+03:00")
        x += 30
    assert event is not None
    assert event.total_vehicles == 1
    assert event.vehicle_counts.get("car") == 1
    assert event.avg_dwell_s > 0


def test_event_envelope_shape() -> None:
    pipeline = _pipeline()
    x = 200
    event = None
    for seq in range(3):
        event = pipeline.process(make_frame([(x, 300, 70, 40, CAR_BGR)]), seq, "t")
        x += 30
    assert event is not None
    envelope = event.to_envelope()
    assert envelope["segment_id"] == "jaffa-road-00"
    assert "vehicle_counts" in envelope
    assert "incidents" in envelope
    assert isinstance(envelope["tracks"], list)


def test_decode_frame_roundtrip() -> None:
    frame = make_frame([(200, 300, 70, 40, CAR_BGR)])
    ok, buf = cv2.imencode(".jpg", frame)
    assert ok
    b64 = base64.b64encode(buf.tobytes()).decode("ascii")
    decoded = decode_frame(b64)
    assert decoded.shape == frame.shape


def test_annotate_and_encode_png() -> None:
    pipeline = _pipeline()
    frame = make_frame([(200, 300, 70, 40, CAR_BGR)])
    for seq in range(3):
        event = pipeline.process(frame, seq, "t")
    png = encode_png(annotate(frame, event))
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
