from pathlib import Path

from camera_simulator.frames import Frame
from camera_simulator.publishers import FileFramePublisher
from camera_simulator.runner import Camera, CameraRunner, CameraSpec
from camera_simulator.scene import IncidentKind, SceneConfig


class _Capture:
    def __init__(self) -> None:
        self.frames: list[Frame] = []

    def publish(self, frame: Frame) -> None:
        self.frames.append(frame)

    def close(self) -> None:
        return None


def _camera(camera_id: str, seed: int) -> Camera:
    return Camera(
        CameraSpec(camera_id, camera_id.removeprefix("C-"), SceneConfig(density=1.0, seed=seed))
    )


def test_runner_emits_one_frame_per_camera_per_tick() -> None:
    cameras = [_camera("C-a", 1), _camera("C-b", 2)]
    capture = _Capture()
    runner = CameraRunner(cameras, capture, fps=30)
    produced = runner.run(max_frames=20)
    assert produced == 20
    assert len(capture.frames) == 20
    assert {f.camera_id for f in capture.frames} == {"C-a", "C-b"}


def test_frame_envelope_has_base64_image() -> None:
    capture = _Capture()
    runner = CameraRunner([_camera("C-a", 1)], capture, fps=30)
    runner.run(max_frames=1)
    envelope = capture.frames[0].to_envelope()
    assert envelope["format"] == "jpeg"
    assert isinstance(envelope["image_b64"], str)
    assert envelope["width"] == 1280
    assert envelope["height"] == 720


def test_injected_incident_appears_in_frame_hints() -> None:
    cameras = [_camera("C-a", 1)]
    capture = _Capture()
    runner = CameraRunner(cameras, capture, fps=30)
    runner.inject("C-a", IncidentKind.STOPPED_VEHICLE)
    runner.run(max_frames=1)
    assert "stopped_vehicle" in capture.frames[0].incident_hints


def test_file_publisher_writes_frames(tmp_path: Path) -> None:
    publisher = FileFramePublisher(tmp_path)
    runner = CameraRunner([_camera("C-a", 1)], publisher, fps=30)
    runner.run(max_frames=3)
    written = sorted(tmp_path.glob("*.jpg"))
    assert len(written) == 3
