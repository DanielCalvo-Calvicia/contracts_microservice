from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class StepperCompletedInboundEventDTO:
    pass

@dataclass(slots=True, frozen=True)
class StepperCompletedInboundEvent(BaseEvent[StepperCompletedInboundEventDTO]):
    type: str = "completed"

