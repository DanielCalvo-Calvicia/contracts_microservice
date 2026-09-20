from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class STTCompletedOutboundEventDTO:
    reason: str
    output: str

@dataclass(slots=True, frozen=True)
class STTCompletedOutboundEvent(BaseEvent[STTCompletedOutboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

