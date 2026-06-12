from vision_service.detection import Detection
from vision_service.tracking import ByteTrackConfig, ByteTracker, TrackState, iou


def det(x: float, y: float = 300.0, conf: float = 0.9, label: str = "car") -> Detection:
    return Detection(x, y, 60.0, 40.0, label, conf)


def test_iou_basic() -> None:
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert 0.0 < iou((0, 0, 10, 10), (5, 5, 15, 15)) < 1.0


def test_track_confirmed_after_min_hits() -> None:
    tracker = ByteTracker(ByteTrackConfig(min_hits=3))
    x = 100.0
    for _ in range(2):
        tracker.step([det(x)])
        x += 10
    assert tracker.tracks == []  # still tentative
    tracker.step([det(x)])
    assert len(tracker.tracks) == 1
    assert tracker.tracks[0].state is TrackState.CONFIRMED


def test_stable_id_across_motion() -> None:
    tracker = ByteTracker(ByteTrackConfig(min_hits=2))
    x = 100.0
    ids = set()
    for _ in range(15):
        tracker.step([det(x)])
        x += 12
        if tracker.tracks:
            ids.add(tracker.tracks[0].track_id)
    assert ids == {1}  # one identity throughout


def test_low_confidence_recovers_track() -> None:
    """A track shouldn't die when its detection score briefly dips (ByteTrack)."""
    tracker = ByteTracker(ByteTrackConfig(min_hits=2, high_thresh=0.5, low_thresh=0.1))
    x = 100.0
    for _ in range(4):
        tracker.step([det(x, conf=0.9)])
        x += 10
    track_id = tracker.tracks[0].track_id
    # Now only a low-confidence detection arrives — stage 2 should keep the id.
    tracker.step([det(x, conf=0.2)])
    x += 10
    assert tracker.tracks and tracker.tracks[0].track_id == track_id


def test_lost_track_reaped_after_max_age() -> None:
    tracker = ByteTracker(ByteTrackConfig(min_hits=2, max_age=5))
    x = 100.0
    for _ in range(3):
        tracker.step([det(x)])
        x += 10
    for _ in range(6):
        tracker.step([])  # no detections
    assert tracker.all_tracks == []


def test_two_objects_get_distinct_ids() -> None:
    tracker = ByteTracker(ByteTrackConfig(min_hits=2))
    xa, xb = 100.0, 600.0
    for _ in range(4):
        tracker.step([det(xa), det(xb)])
        xa += 10
        xb += 10
    assert len({t.track_id for t in tracker.tracks}) == 2
