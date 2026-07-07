from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class SpeakerPartialInboundEventDTO:
    bytes_base64: str


@dataclass(slots=True, frozen=True)
class SpeakerPartialInboundEvent(BaseEvent[SpeakerPartialInboundEventDTO]):
    type: str = "partial"