from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class TTSPartialInboundEventDTO:
    text: str


@dataclass(slots=True, frozen=True)
class TTSPartialInboundEvent(BaseEvent[TTSPartialInboundEventDTO]):
    type: str = "partial"