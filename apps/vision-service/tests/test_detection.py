from _frames import CAR_BGR, TRUCK_BGR, make_frame

from vision_service.detection import SyntheticDetector, build_detector


def test_synthetic_detector_finds_sprites() -> None:
    frame = make_frame([(200, 300, 70, 40, CAR_BGR), (600, 400, 120, 50, TRUCK_BGR)])
    detections = SyntheticDetector().detect(frame)
    labels = sorted(d.label for d in detections)
    assert labels == ["car", "truck"]


def test_synthetic_detector_returns_reasonable_boxes() -> None:
    frame = make_frame([(200, 300, 70, 40, CAR_BGR)])
    (detection,) = SyntheticDetector().detect(frame)
    assert abs(detection.x - 200) < 5
    assert abs(detection.w - 70) < 6
    assert detection.confidence > 0.5


def test_empty_road_yields_no_detections() -> None:
    frame = make_frame([])
    assert SyntheticDetector().detect(frame) == []


def test_build_detector_factory() -> None:
    assert isinstance(build_detector("synthetic", "x", 0.3), SyntheticDetector)
    # yolo path constructs without loading weights (lazy) — just type-checks here.
    yolo = build_detector("yolo", "yolov8n.pt", 0.3)
    assert yolo.__class__.__name__ == "YoloDetector"


def test_unknown_detector_raises() -> None:
    try:
        build_detector("nope", "x", 0.3)
    except ValueError as exc:
        assert "nope" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")
