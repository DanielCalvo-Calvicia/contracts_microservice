from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class STTProcessBatchStartRequestDTO:
    audio_data: bytes
    sample_rate: int = 16000


@dataclass(slots=True, frozen=True)
class STTProcessBatchStartRequest(BaseRequest[STTProcessBatchStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class STTProcessBatchStartResponseDTO:
    text: str


@dataclass(slots=True, frozen=True)
class STTProcessBatchStartResponse(BaseResponse[STTProcessBatchStartResponseDTO]):
    pass