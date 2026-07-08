from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent

@dataclass(slots=True, frozen=True)
class StepperPartialInboundEventDTO:
    action: str
    rotations: float
    rpm: int
    direction: str


@dataclass(slots=True, frozen=True)
class StepperPartialInboundEvent(BaseEvent[StepperPartialInboundEventDTO]):
    type: str = "partial"