from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class STTProcessStreamStartRequestDTO:
    audio_stream: AsyncIterator[bytes]
    sample_rate: int = 16000
    chunk_size: int = 1024
    silence_threshold: int = 150
    silence_limit_seconds: float = 2.0


@dataclass(slots=True, frozen=True)
class STTProcessStreamStartRequest(BaseRequest[STTProcessStreamStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class STTProcessStreamStartResponseDTO:
    text_stream: AsyncIterator[str]


@dataclass(slots=True, frozen=True)
class STTProcessStreamStartResponse(BaseResponse[STTProcessStreamStartResponseDTO]):
    pass