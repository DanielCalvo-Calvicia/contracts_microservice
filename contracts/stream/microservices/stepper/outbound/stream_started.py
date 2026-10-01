from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class StepperStreamStartedOutboundEventDTO:
    """The motor is known and free: the service is consuming commands for it."""

    message: str


@dataclass(frozen=True, slots=True)
class StepperStreamStartedOutboundEvent(BaseEvent[StepperStreamStartedOutboundEventDTO]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )
