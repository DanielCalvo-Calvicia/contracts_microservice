from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True, frozen=True)
class MotorDirective:
    """A physical arm-movement request ai-agent hands to Brain.

    ai-agent never calls stepper itself: Brain is the only service allowed to act on this,
    by translating it into a ``contracts.api.microservices.stepper`` command.
    """

    arm: Literal["left", "right"]
    degrees: float
    direction: Literal["forward", "reverse"] = "forward"
