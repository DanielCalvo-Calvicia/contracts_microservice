from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class SpeakerCompletedEventDTO:
    reason: str
    total_bytes_consumed: int
    message: str

@dataclass(slots=True, frozen=True)
class SpeakerCompletedEvent(BaseEvent[SpeakerCompletedEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

