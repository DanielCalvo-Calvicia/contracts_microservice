from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.session import SessionCreateRequest, SessionCreateResponse


@dataclass(slots=True, frozen=True)
class STTStreamConfig:
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    language: Optional[str] = None
    model: Optional[str] = None
    silence_threshold: int = 150
    silence_limit_seconds: float = 2.0


@dataclass(slots=True, frozen=True)
class STTProcessStreamSessionRequest(SessionCreateRequest[STTStreamConfig]):
    pass


@dataclass(slots=True, frozen=True)
class STTProcessStreamSessionResponse(SessionCreateResponse):
    accepted_config: STTStreamConfig = STTStreamConfig()
