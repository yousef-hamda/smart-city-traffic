from vision_service.incidents import IncidentDetector, IncidentKind
from vision_service.tracking import Track, TrackState


def _confirmed(track_id: int, vx: float, history: list[tuple[int, float, float]]) -> Track:
    last = history[-1]
    return Track(
        track_id=track_id,
        label="car",
        cx=last[1],
        cy=last[2],
        w=60.0,
        h=40.0,
        vx=vx,
        state=TrackState.CONFIRMED,
        history=history,
    )


def test_stopped_vehicle_detected() -> None:
    detector = IncidentDetector(fps=2.0, stopped_seconds=4.0)  # window = 8 frames
    # 10 frames barely moving.
    history = [(i, 500.0 + (i % 2) * 0.5, 300.0) for i in range(10)]
    track = _confirmed(1, vx=0.0, history=history)
    kinds = {i.kind for i in detector.detect([track])}
    assert IncidentKind.STOPPED_VEHICLE in kinds


def test_moving_vehicle_not_flagged_stopped() -> None:
    detector = IncidentDetector(fps=2.0, stopped_seconds=4.0)
    history = [(i, 100.0 + i * 20.0, 300.0) for i in range(10)]
    track = _confirmed(1, vx=20.0, history=history)
    kinds = {i.kind for i in detector.detect([track])}
    assert IncidentKind.STOPPED_VEHICLE not in kinds


def test_wrong_way_detected_against_flow() -> None:
    detector = IncidentDetector(fps=15.0)
    forward = [
        _confirmed(i, vx=5.0, history=[(0, 100.0, 300.0), (1, 105.0, 300.0)])
        for i in range(2, 6)
    ]
    against = _confirmed(1, vx=-4.0, history=[(0, 800.0, 300.0), (1, 796.0, 300.0)])
    incidents = detector.detect([*forward, against])
    wrong = [i for i in incidents if i.kind is IncidentKind.WRONG_WAY]
    assert any(i.track_id == 1 for i in wrong)


def test_sudden_lane_change_detected() -> None:
    detector = IncidentDetector(fps=15.0, lane_change_window=8, lane_change_ratio=1.2)
    # Vertical jump of ~60px with height 40 → ratio 1.5 > 1.2.
    history = [(i, 400.0, 300.0 + i * 8.0) for i in range(8)]
    track = _confirmed(1, vx=2.0, history=history)
    kinds = {i.kind for i in detector.detect([track])}
    assert IncidentKind.SUDDEN_LANE_CHANGE in kinds
