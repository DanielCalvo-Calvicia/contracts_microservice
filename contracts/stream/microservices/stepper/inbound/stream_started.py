from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class StepperStreamStartedInboundEventDTO:
    """The sender opens a command stream for one stepper motor."""

    stepper_id: str


@dataclass(frozen=True, slots=True)
class StepperStreamStartedInboundEvent(BaseEvent[StepperStreamStartedInboundEventDTO]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )
