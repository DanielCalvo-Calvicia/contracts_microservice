from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class SpeakerCompletedInboundEventDTO:
    pass

@dataclass(slots=True, frozen=True)
class SpeakerCompletedInboundEvent(BaseEvent[SpeakerCompletedInboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

