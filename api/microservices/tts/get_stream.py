from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class TTSGetStreamRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class TTSGetStreamRequest(BaseRequest[TTSGetStreamRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class TTSGetStreamResponseDTO:
    audio_stream: AsyncIterator[bytes]


@dataclass(slots=True, frozen=True)
class TTSGetStreamResponse(BaseResponse[TTSGetStreamResponseDTO]):
    pass