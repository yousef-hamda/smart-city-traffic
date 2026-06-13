"""Text-to-speech interface and implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

# Minimal valid ID3v2 header used as a silent MP3 placeholder.
_SILENT_MP3_PLACEHOLDER: bytes = b"ID3" + b"\x00" * 100


class TTSBase(ABC):
    """Abstract base class for text-to-speech backends."""

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Synthesize *text* into audio bytes (MP3)."""
        ...


class FakeTTS(TTSBase):
    """For tests — returns a silent placeholder MP3 without any I/O."""

    def synthesize(self, text: str) -> bytes:  # noqa: ARG002
        return _SILENT_MP3_PLACEHOLDER


class OfflineTTS(TTSBase):
    """Offline stub — returns a placeholder when no cloud API key is configured.

    In a production deployment this would drive pyttsx3 for genuine on-device
    synthesis, but the binary output of pyttsx3 is platform-dependent and not
    suitable as a streaming HTTP response without additional transcoding.  The
    placeholder keeps the service functional and lets integration tests run
    without any audio libraries.
    """

    def synthesize(self, text: str) -> bytes:  # noqa: ARG002
        return _SILENT_MP3_PLACEHOLDER


class OpenAITTS(TTSBase):
    """OpenAI TTS — only instantiated when ``OPENAI_API_KEY`` is set."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def synthesize(self, text: str) -> bytes:  # noqa: ARG002
        # Real implementation would call the OpenAI /audio/speech endpoint.
        # Placeholder keeps the interface correct until the key is wired.
        return _SILENT_MP3_PLACEHOLDER


def get_tts_client(openai_api_key: str = "") -> TTSBase:
    """Factory: returns :class:`OpenAITTS` when a key is present, else :class:`OfflineTTS`."""
    if openai_api_key:
        return OpenAITTS(openai_api_key)
    return OfflineTTS()
