from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class STTPartialInboundEventDTO:
    bytes_base64: str


@dataclass(slots=True, frozen=True)
class STTPartialInboundEvent(BaseEvent[STTPartialInboundEventDTO]):
    type: str = "partial"