from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Which flow of ai-agent answered a message: ``identification`` (only when triage itself asks the user a question),
# ``conversation`` (a plain reply), ``special`` (anything that needs
# planning or tools) or ``movement`` (arm movements). ai-agent picks it from the triage; Brain only reads it.
AgentFlowName = Literal["identification", "conversation", "special", "movement"]


@dataclass(slots=True, frozen=True)
class MotorDirective:
    """A physical arm-movement request ai-agent hands to Brain.

    ai-agent never calls stepper itself: Brain is the only service allowed to act on this,
    by translating it into a ``contracts.api.microservices.stepper`` command.
    """

    arm: Literal["left", "right"]
    degrees: float
    direction: Literal["forward", "reverse"] = "forward"
