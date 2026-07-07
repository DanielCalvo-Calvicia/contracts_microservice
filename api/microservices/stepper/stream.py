from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class StepperStreamRequestDTO:
    stepper_id: str
    command_stream: AsyncIterator[dict[str, Any]]
    #setup_future: asyncio.Future[Any] | None = None


@dataclass(slots=True, frozen=True)
class StepperStreamRequest(BaseRequest[StepperStreamRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class StepperStreamResponseDTO:
    success: bool
    message: str


@dataclass(slots=True, frozen=True)
class StepperStreamResponse(BaseResponse[StepperStreamResponseDTO]):
    pass