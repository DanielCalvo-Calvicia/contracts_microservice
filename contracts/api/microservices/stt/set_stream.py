from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class STTSetStreamStartRequestDTO:
    audio_stream: AsyncIterator[bytes]
    sample_rate: int = 16000
    chunk_size: int = 1024
    silence_threshold: int = 150
    silence_limit_seconds: float = 2.0



@dataclass(slots=True, frozen=True)
class STTSetStreamStartRequest(BaseRequest[STTSetStreamStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class STTSetStreamStartResponseDTO:
    accepted: bool


@dataclass(slots=True, frozen=True)
class STTSetStreamStartResponse(BaseResponse[STTSetStreamStartResponseDTO]):
    pass