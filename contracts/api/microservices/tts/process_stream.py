from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.session import SessionCreateRequest, SessionCreateResponse


@dataclass(slots=True, frozen=True)
class TTSStreamConfig:
    sample_rate: int = 22050
    channels: int = 1
    language: Optional[str] = None
    voice: Optional[str] = None
    model: Optional[str] = None
    text_encoding: str = "utf-8"


@dataclass(slots=True, frozen=True)
class TTSProcessStreamSessionRequest(SessionCreateRequest[TTSStreamConfig]):
    pass


@dataclass(slots=True, frozen=True)
class TTSProcessStreamSessionResponse(SessionCreateResponse):
    accepted_config: TTSStreamConfig = TTSStreamConfig()
