from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.stream import StreamDirection


@dataclass(slots=True, frozen=True)
class TTSGetStreamRequest:
    session_id: str
    direction: StreamDirection = "outbound"
    encoding: str = "pcm16"
    from_sequence: Optional[int] = None


@dataclass(slots=True, frozen=True)
class TTSGetStreamResponse:
    session_id: str
    stream_ready: bool
    media_type: str = "audio/L16"
    message: str = "ready"
