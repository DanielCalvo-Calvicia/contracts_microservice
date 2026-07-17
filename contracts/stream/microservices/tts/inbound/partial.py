from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from dataclasses import field

from contracts.stream.common.base import BaseEvent, EventType

@dataclass(slots=True, frozen=True)
class PartialInboundEventDTO:
    text: str


@dataclass(slots=True, frozen=True)
class PartialInboundEvent(BaseEvent[PartialInboundEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )