from __future__ import annotations

from dataclasses import dataclass

from stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class StepperCompletedOutboundEventDTO:
    message: str

@dataclass(slots=True, frozen=True)
class StepperCompletedOutboundEvent(BaseEvent[StepperCompletedOutboundEventDTO]):
    type: str = "completed"

