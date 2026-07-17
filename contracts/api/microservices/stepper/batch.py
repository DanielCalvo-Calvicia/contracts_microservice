from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True, frozen=True)
class StepperBatchCommand:
    stepper_id: str
    action: Literal["rotate", "steps", "stop"]
    value: float = 0.0
    speed: float = 0.0
    direction: Literal["forward", "reverse"] = "forward"


@dataclass(slots=True, frozen=True)
class StepperBatchResult:
    success: bool
    message: str
