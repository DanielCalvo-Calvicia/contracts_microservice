from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class TTSProcessBatchRequestDTO:
    text: str
    sample_rate: int = 22050
    channels: int = 1


@dataclass(slots=True, frozen=True)
class TTSProcessBatchRequest(BaseRequest[TTSProcessBatchRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class TTSProcessBatchResponseDTO:
    audio_data: bytes


@dataclass(slots=True, frozen=True)
class TTSProcessBatchResponse(BaseResponse[TTSProcessBatchResponseDTO]):
    pass