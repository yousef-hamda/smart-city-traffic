"""Test fixtures and a critical performance guard.

On many-core machines, PyTorch/OpenMP oversubscribe threads for the tiny
batches these tests use, so repeated LSTM trainings thrash the scheduler and
each `Trainer.fit` crawls. Pinning to a single thread turns the deep-learning
tests from minutes into seconds with no effect on correctness — the models are
deliberately small. This also keeps CI fast and deterministic.
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

try:
    import torch

    torch.set_num_threads(1)
except ImportError:  # pragma: no cover - torch always present in this service
    pass
