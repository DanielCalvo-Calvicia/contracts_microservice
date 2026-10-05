from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class STTCompletedOutboundEventDTO:
    reason: str
    output: str
    # The utterance this text is the transcription of, as PCM16 mono at the sample rate of the input stream, base64.
    # Empty unless the STT stream was asked to return it (the wake-phrase gate: Brain forwards the audio of an
    # utterance that carried the phrase to the real engine).
    audio_base64: str = ""

@dataclass(slots=True, frozen=True)
class STTCompletedOutboundEvent(BaseEvent[STTCompletedOutboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )
