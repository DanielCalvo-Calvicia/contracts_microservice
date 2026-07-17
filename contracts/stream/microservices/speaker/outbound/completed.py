from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class SpeakerCompletedOutboundEventDTO:
    reason: str
    output: str
    chunk_count: str
    byte_count: int
    message: str

@dataclass(slots=True, frozen=True)
class SpeakerCompletedOutboundEvent(BaseEvent[SpeakerCompletedOutboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

