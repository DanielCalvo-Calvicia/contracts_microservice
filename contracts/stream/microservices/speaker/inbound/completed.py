from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class SpeakerCompletedInboundEventDTO:
    pass

@dataclass(slots=True, frozen=True)
class SpeakerCompletedInboundEvent(BaseEvent[SpeakerCompletedInboundEventDTO]):
    type: str = "completed"

