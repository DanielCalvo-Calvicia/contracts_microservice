from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class SpeakerCompletedOutboundEventDTO:
    reason: str
    output: str
    chunk_count: str
    byte_count: int
    message: str

@dataclass(slots=True, frozen=True)
class SpeakerCompletedOutboundEvent(BaseEvent[SpeakerCompletedOutboundEventDTO]):
    type: str = "completed"

