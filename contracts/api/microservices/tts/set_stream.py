from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class TTSSetStreamRequestDTO:
    text_stream: AsyncIterator[str]
    sample_rate: int = 22050
    channels: int = 1


@dataclass(slots=True, frozen=True)
class TTSSetStreamRequest(BaseRequest[TTSSetStreamRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class TTSSetStreamResponseDTO:
    content: AsyncIterator[str] | AsyncIterator[bytes]
    media_type: str
    status_code: int
    headers: dict[str, str]

@dataclass(slots=True, frozen=True)
class TTSSetStreamResponse(TTSSetStreamResponseDTO):
    pass