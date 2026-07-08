from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class TTSCompletedInboundEventDTO:
    reason: str
    output: str

@dataclass(slots=True, frozen=True)
class TTSCompletedInboundEvent(BaseEvent[TTSCompletedInboundEventDTO]):
    type: str = "completed"

