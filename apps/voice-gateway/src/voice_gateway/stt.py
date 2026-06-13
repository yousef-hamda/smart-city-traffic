"""Speech-to-text interface and implementations."""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Any


class STTBase(ABC):
    """Abstract base class for speech-to-text backends."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes to text."""
        ...


class FakeSTT(STTBase):
    """For tests — returns a fixed transcription without downloading any model."""

    def transcribe(self, audio_bytes: bytes) -> str:  # noqa: ARG002
        return "fake transcription result"


class WhisperSTT(STTBase):
    """Production STT using faster-whisper — model is lazy-loaded on first call."""

    def __init__(self, model_name: str = "tiny") -> None:
        self._model_name = model_name
        self._model: Any = None  # Any because faster_whisper has no stubs

    def _get_model(self) -> Any:
        if self._model is None:
            # Import here so pytest never triggers a model download at import time.
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self._model_name, device="cpu", compute_type="int8")
        return self._model

    def transcribe(self, audio_bytes: bytes) -> str:
        model: Any = self._get_model()
        audio_file = io.BytesIO(audio_bytes)
        # faster_whisper.WhisperModel.transcribe returns (segments, info)
        segments, _ = model.transcribe(audio_file)
        return " ".join(s.text for s in segments)
