from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class STTCompletedInboundEventDTO:
    reason: str
    output: str

@dataclass(slots=True, frozen=True)
class STTCompletedInboundEvent(BaseEvent[STTCompletedInboundEventDTO]):
    type: str = "completed"

