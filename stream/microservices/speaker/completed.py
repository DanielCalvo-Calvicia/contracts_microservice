from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class SpeakerCompletedEventDTO:
    reason: str
    total_bytes_consumed: int
    message: str

@dataclass(slots=True, frozen=True)
class SpeakerCompletedEvent(BaseEvent[SpeakerCompletedEventDTO]):
    type: str = "completed"

