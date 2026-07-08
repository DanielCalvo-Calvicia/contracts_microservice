from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class StepperBatchStartRequestDTO:
    stepper_id: str
    action: str  # 'rotate', 'steps', 'stop'
    value: float = 0.0  # rotate -> full revolutions; steps -> number of steps
    speed: float = 0.0  # rotate -> RPM; steps -> steps per second
    direction: str = "forward"  # 'forward' or 'reverse'

@dataclass(slots=True, frozen=True)
class StepperBatchStartRequest(BaseRequest[StepperBatchStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class StepperBatchStartResponseDTO:
    success: bool
    message: str


@dataclass(slots=True, frozen=True)
class StepperBatchStartResponse(BaseResponse[StepperBatchStartResponseDTO]):
    pass