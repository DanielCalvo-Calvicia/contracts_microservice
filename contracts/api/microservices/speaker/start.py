from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from contracts.api.common.session import SessionCreateRequest, SessionCreateResponse


@dataclass(slots=True, frozen=True)
class SpeakerConfig:
    sample_rate: int = 24000
    channels: int = 1
    encoding: str = "pcm16"
    output_device_id: Optional[str] = None


@dataclass(slots=True, frozen=True)
class SpeakerStartSessionRequest(SessionCreateRequest[SpeakerConfig]):
    pass


@dataclass(slots=True, frozen=True)
class SpeakerStartSessionResponse(SessionCreateResponse):
    accepted_config: SpeakerConfig = SpeakerConfig()
