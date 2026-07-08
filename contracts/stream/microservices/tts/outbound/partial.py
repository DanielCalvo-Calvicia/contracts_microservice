from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class TTSPartialOutboundEventDTO:
    bytes_base64: str
    byte_count: int
    chunk_index: int


@dataclass(slots=True, frozen=True)
class TTSPartialOutboundEvent(BaseEvent[TTSPartialOutboundEventDTO]):
    type: str = "partial"