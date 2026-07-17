from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType

@dataclass(slots=True, frozen=True)
class SpeakerPartialEventDTO:
    status: str
    bytes_consumed: int
    chunks_processed: int


@dataclass(slots=True, frozen=True)
class SpeakerPartialEvent(BaseEvent[SpeakerPartialEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )