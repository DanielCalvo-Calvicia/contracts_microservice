from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.session import SessionCreateRequest, SessionCreateResponse


@dataclass(slots=True, frozen=True)
class MicrophoneConfig:
    sample_rate: int = 16000
    channels: int = 1
    encoding: str = "pcm16"
    frame_ms: int = 20
    device_id: Optional[str] = None


@dataclass(slots=True, frozen=True)
class MicrophoneStartSessionRequest(SessionCreateRequest[MicrophoneConfig]):
    pass


@dataclass(slots=True, frozen=True)
class MicrophoneStartSessionResponse(SessionCreateResponse):
    accepted_config: MicrophoneConfig = MicrophoneConfig()
