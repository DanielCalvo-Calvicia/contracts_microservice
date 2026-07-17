from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.stream import StreamDirection


@dataclass(slots=True, frozen=True)
class STTGetStreamRequest:
    session_id: str
    direction: StreamDirection = "outbound"
    encoding: str = "utf-8"
    include_partials: bool = True
    from_sequence: Optional[int] = None


@dataclass(slots=True, frozen=True)
class STTGetStreamResponse:
    session_id: str
    stream_ready: bool
    message: str
