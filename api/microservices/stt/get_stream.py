from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class STTGetStreamStartRequestDTO:
    pass


@dataclass(slots=True, frozen=True)
class STTGetStreamStartRequest(BaseRequest[STTGetStreamStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class STTGetStreamStartResponseDTO:
    text_stream: AsyncIterator[str]


@dataclass(slots=True, frozen=True)
class STTGetStreamStartResponse(BaseResponse[STTGetStreamStartResponseDTO]):
    pass