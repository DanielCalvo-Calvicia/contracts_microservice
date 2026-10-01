from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(slots=True, frozen=True)
class MotorDirective:
    """A physical arm-movement request ai-agent hands to Brain.

    ai-agent never calls stepper itself: Brain is the only service allowed to act on this,
    by translating it into a ``contracts.api.microservices.stepper`` command.
    """

    arm: Literal["left", "right"]
    degrees: float
    direction: Literal["forward", "reverse"] = "forward"


@dataclass(slots=True, frozen=True)
class RobotContext:
    """What motion-flow decided for a message, so conversation-flow can word its reply truthfully.

    Brain gets it from motion-flow and forwards it with the message it sends to conversation-flow.
    ``directives`` is the accepted movement sequence, in execution order (empty when there is none).
    ``rejected_reason`` says why a requested movement cannot be done (spoken as a refusal, never as done).
    """

    directives: tuple[MotorDirective, ...] = ()
    rejected_reason: Optional[str] = None
