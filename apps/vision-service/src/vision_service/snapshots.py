"""Latest annotated frame per segment, for the ``/snapshot`` endpoint.

In-memory and thread-safe: the Kafka consumer thread writes, FastAPI request
handlers read. A bounded store keeps only the most recent annotated PNG per
segment — historical frames belong in the lake, not in service memory.
"""

import threading


class SnapshotStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_segment: dict[str, bytes] = {}
        self._seq_by_segment: dict[str, int] = {}

    def put(self, segment_id: str, seq: int, png: bytes) -> None:
        with self._lock:
            self._by_segment[segment_id] = png
            self._seq_by_segment[segment_id] = seq

    def get(self, segment_id: str) -> bytes | None:
        with self._lock:
            return self._by_segment.get(segment_id)

    def segments(self) -> list[str]:
        with self._lock:
            return sorted(self._by_segment)
