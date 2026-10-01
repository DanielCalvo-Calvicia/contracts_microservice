from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class StepperPartialInboundEventDTO:
    """One motor command, the same three actions as the batch routes.

    * ``rotate``: ``rotations`` full revolutions at ``rpm``.
    * ``steps``: ``steps`` raw steps at ``speed`` steps per second.
    * ``stop``: emergency stop of the motor (the other fields are ignored).

    ``direction`` is ``forward`` or ``reverse``. A speed of 0 means the service's default speed limit.
    """

    action: str
    rotations: float = 0.0
    steps: float = 0.0
    rpm: float = 0.0
    speed: float = 0.0
    direction: str = "forward"


@dataclass(slots=True, frozen=True)
class StepperPartialInboundEvent(BaseEvent[StepperPartialInboundEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )
