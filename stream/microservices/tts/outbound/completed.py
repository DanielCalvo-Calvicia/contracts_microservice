from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class TTSCompletedOutboundEventDTO:
    reason: str
    output_bytes_base64: str
    total_bytes: int
    chunk_count: int

@dataclass(slots=True, frozen=True)
class TTSCompletedOutboundEvent(BaseEvent[TTSCompletedOutboundEventDTO]):
    type: str = "completed"

