from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.session import SessionCreateRequest, SessionCreateResponse


@dataclass(slots=True, frozen=True)
class STTStreamConfig:
    sample_rate: int = 16000
    channels: int = 1
    language: Optional[str] = None
    model: Optional[str] = None


@dataclass(slots=True, frozen=True)
class STTProcessStreamSessionRequest(SessionCreateRequest[STTStreamConfig]):
    pass


@dataclass(slots=True, frozen=True)
class STTProcessStreamSessionResponse(SessionCreateResponse):
    accepted_config: STTStreamConfig = STTStreamConfig()
