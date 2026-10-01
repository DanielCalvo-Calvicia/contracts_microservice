from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class StepperPartialOutboundEventDTO:
    """The outcome of one command of the stream, in the order the commands arrived."""

    action: str
    success: bool
    message: str


@dataclass(slots=True, frozen=True)
class StepperPartialOutboundEvent(BaseEvent[StepperPartialOutboundEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )
