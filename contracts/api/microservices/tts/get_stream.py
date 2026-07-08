from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from contracts.api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class TTSGetStreamRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class TTSGetStreamRequest(BaseRequest[TTSGetStreamRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class TTSGetStreamResponseDTO:
    content: AsyncIterator[str] | AsyncIterator[bytes]
    media_type: str
    status_code: int
    headers: dict[str, str]



@dataclass(slots=True, frozen=True)
class TTSGetStreamResponse(TTSGetStreamResponseDTO):
    pass