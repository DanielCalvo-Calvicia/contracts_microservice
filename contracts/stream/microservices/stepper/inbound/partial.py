from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType

@dataclass(slots=True, frozen=True)
class StepperPartialInboundEventDTO:
    action: str
    rotations: float
    rpm: int
    direction: str


@dataclass(slots=True, frozen=True)
class StepperPartialInboundEvent(BaseEvent[StepperPartialInboundEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )