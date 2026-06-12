"""Shared fixtures built on the synthetic frame helpers in ``_frames``."""

import numpy as np
import pytest
from _frames import CAR_BGR, make_frame


@pytest.fixture
def car_frame_factory():
    def _factory(x: int, y: int = 300) -> np.ndarray:
        return make_frame([(x, y, 70, 40, CAR_BGR)])

    return _factory
