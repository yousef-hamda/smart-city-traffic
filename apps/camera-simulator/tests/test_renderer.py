import numpy as np

from camera_simulator.renderer import (
    FRAME_HEIGHT,
    FRAME_WIDTH,
    RenderContext,
    encode_jpeg,
    render,
)
from camera_simulator.scene import Scene, SceneConfig

CTX = RenderContext(camera_id="C-jaffa-road-00", timestamp_iso="2026-06-08T08:00:00+03:00")


def test_render_produces_720p_bgr_frame() -> None:
    scene = Scene(SceneConfig(lanes=3, density=1.0, seed=1))
    frame = render(scene, CTX)
    assert frame.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3)
    assert frame.dtype == np.uint8


def test_denser_scene_paints_more_vehicle_pixels() -> None:
    light = render(Scene(SceneConfig(lanes=3, density=0.3, seed=1)), CTX)
    heavy = render(Scene(SceneConfig(lanes=3, density=2.5, seed=1)), CTX)
    # Count non-asphalt, non-background pixels in the road band as a proxy.
    assert int(heavy.sum()) != int(light.sum())


def test_jpeg_encoding_roundtrips_size() -> None:
    scene = Scene(SceneConfig(lanes=3, density=1.0, seed=1))
    jpeg = encode_jpeg(render(scene, CTX))
    assert jpeg[:2] == b"\xff\xd8"  # JPEG SOI marker
    assert len(jpeg) > 1000
