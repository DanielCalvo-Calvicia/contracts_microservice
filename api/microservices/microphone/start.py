from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class MicrophoneStartRequestDTO:
    sample_rate: int = 16000
    channels: int = 1
    format: str = "pcm16"


@dataclass(slots=True, frozen=True)
class MicrophoneStartRequest(BaseRequest[MicrophoneStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class MicrophoneStartResponseDTO:
    stream: AsyncIterator[bytes]
    sample_rate: int


@dataclass(slots=True, frozen=True)
class MicrophoneStartResponse(BaseResponse[MicrophoneStartResponseDTO]):
    pass