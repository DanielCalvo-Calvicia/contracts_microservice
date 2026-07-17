from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from dataclasses import field
from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class TTSCompletedInboundEventDTO:
    reason: str
    output: str

@dataclass(slots=True, frozen=True)
class TTSCompletedInboundEvent(BaseEvent[TTSCompletedInboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

