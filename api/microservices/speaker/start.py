from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Protocol, Optional

from api.common.base import BaseRequest, BaseResponse


@dataclass(slots=True, frozen=True)
class SpeakerStartRequestDTO:
    """Inbound client payload delivering raw audio chunks."""
    audio_stream: AsyncIterator[bytes]
    sample_rate: int = 24000
    channels: int = 1
    #setup_future: asyncio.Future[PlaybackStreamResponseDto] | None = None


@dataclass(slots=True, frozen=True)
class SpeakerStartRequest(BaseRequest[SpeakerStartRequestDTO]):
    pass


@dataclass(slots=True, frozen=True)
class SpeakerStartResponseDTO:
    success: bool
    message: str


@dataclass(slots=True, frozen=True)
class SpeakerStartResponse(BaseResponse[SpeakerStartResponseDTO]):
    pass