"""Tests for WebSocket /voice/stream."""

import json

from fastapi.testclient import TestClient

from voice_gateway.assistant_client import FakeAssistantClient
from voice_gateway.main import create_app, override_assistant, override_stt, override_tts
from voice_gateway.stt import FakeSTT
from voice_gateway.tts import FakeTTS


def test_voice_stream_websocket() -> None:
    override_stt(FakeSTT())
    override_tts(FakeTTS())
    override_assistant(FakeAssistantClient())

    app = create_app()
    client = TestClient(app)

    with client.websocket_connect("/voice/stream") as ws:
        # Send first audio chunk — expect partial transcript back.
        ws.send_bytes(b"audio chunk 1")
        msg = ws.receive_text()
        data = json.loads(msg)
        assert "partial" in data

        # Send second audio chunk.
        ws.send_bytes(b"audio chunk 2")
        partial2 = ws.receive_text()
        assert "partial" in json.loads(partial2)

        # Signal end of audio.
        ws.send_text("END")

        # Receive final transcript.
        final_msg = ws.receive_text()
        final_data = json.loads(final_msg)
        assert "final" in final_data

        # Receive assistant reply (text JSON).
        reply_msg = ws.receive_text()
        reply_data = json.loads(reply_msg)
        assert "assistant_reply" in reply_data

        # Receive synthesized audio bytes before the done signal.
        audio_data = ws.receive_bytes()
        assert len(audio_data) > 0

        # Receive done signal.
        done_msg = ws.receive_text()
        done_data = json.loads(done_msg)
        assert done_data.get("done") is True
