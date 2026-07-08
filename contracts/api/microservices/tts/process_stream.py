from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class TTSProcessBatchRequestDTO:
    text_stream: AsyncIterator[str]
    sample_rate: int = 22050
    channels: int = 1


@dataclass(slots=True, frozen=True)
class TTSProcessBatchRequest(BaseRequest[TTSProcessBatchRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class TTSProcessBatchResponseDTO:
    content: AsyncIterator[str] | AsyncIterator[bytes]
    media_type: str
    status_code: int
    headers: dict[str, str]


@dataclass(slots=True, frozen=True)
class TTSProcessBatchResponse(TTSProcessBatchResponseDTO):
    pass