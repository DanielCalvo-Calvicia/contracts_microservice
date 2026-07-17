from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.session import SessionCreateRequest, SessionCreateResponse
from contracts.api.common.stream import StreamDirection


@dataclass(slots=True, frozen=True)
class StepperStreamConfig:
    stepper_id: str
    command_encoding: str = "json"
    default_direction: str = "forward"
    default_speed: float = 0.0


@dataclass(slots=True, frozen=True)
class StepperStartStreamSessionRequest(SessionCreateRequest[StepperStreamConfig]):
    pass


@dataclass(slots=True, frozen=True)
class StepperStartStreamSessionResponse(SessionCreateResponse):
    accepted_config: StepperStreamConfig


@dataclass(slots=True, frozen=True)
class StepperStreamAttachRequest:
    session_id: str
    direction: StreamDirection = "inbound"
    chunk_bytes: int = 1024
    content_type: Optional[str] = "application/json"


@dataclass(slots=True, frozen=True)
class StepperStreamAttachResponse:
    session_id: str
    accepted: bool
    message: str
