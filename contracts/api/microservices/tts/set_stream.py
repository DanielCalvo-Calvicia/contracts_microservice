from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.stream import StreamDirection


@dataclass(slots=True, frozen=True)
class TTSSetStreamRequest:
    session_id: str
    direction: StreamDirection = "inbound"
    chunk_bytes: int = 1024
    content_type: Optional[str] = "text/plain"


@dataclass(slots=True, frozen=True)
class TTSSetStreamResponse:
    session_id: str
    accepted: bool
    message: str
