from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class SpeakerPartialEventDTO:
    status: str
    bytes_consumed: int
    chunks_processed: int


@dataclass(slots=True, frozen=True)
class SpeakerPartialEvent(BaseEvent[SpeakerPartialEventDTO]):
    type: str = "partial"