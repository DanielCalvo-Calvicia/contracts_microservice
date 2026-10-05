from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class STTUtteranceInboundEventDTO:
    """One finished utterance to transcribe: raw little-endian PCM16 mono at ``sample_rate``, exactly as the
    microphone cut it (Brain passes it on unchanged)."""

    bytes_base64: str
    sample_rate: int


@dataclass(slots=True, frozen=True)
class STTUtteranceInboundEvent(BaseEvent[STTUtteranceInboundEventDTO]):
    type: Literal[EventType.UTTERANCE] = field(
        default=EventType.UTTERANCE,
        init=False,
    )
