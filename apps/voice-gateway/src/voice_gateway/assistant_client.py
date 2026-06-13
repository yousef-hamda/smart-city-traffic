"""HTTP client that forwards transcribed text to the AI-assistant service."""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx


class AssistantClientBase(ABC):
    """Abstract base class for AI-assistant backends."""

    @abstractmethod
    async def chat(self, message: str) -> str:
        """Send *message* and return the assistant's text reply."""
        ...


class FakeAssistantClient(AssistantClientBase):
    """For tests — echoes the message without any network activity."""

    async def chat(self, message: str) -> str:
        return f"Assistant reply to: {message}"


class HTTPAssistantClient(AssistantClientBase):
    """Calls the AI-assistant service over HTTP (POST /chat)."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    async def chat(self, message: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/chat",
                json={"message": message},
                timeout=30.0,
            )
            response.raise_for_status()
            result: str = response.json()["reply"]
            return result
