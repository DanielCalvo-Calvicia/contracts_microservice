from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class STTPartialOutboundEventDTO:
    text: str


@dataclass(slots=True, frozen=True)
class STTPartialOutboundEvent(BaseEvent[STTPartialOutboundEventDTO]):
    type: str = "partial"