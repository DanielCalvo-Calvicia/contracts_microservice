from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class STTCompletedInboundEventDTO:
    output_bytes_base64: str

@dataclass(slots=True, frozen=True)
class STTCompletedInboundEvent(BaseEvent[STTCompletedInboundEventDTO]):
    type: str = "completed"

