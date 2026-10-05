from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class MicrophoneUtteranceEventDTO:
    """One finished utterance: everything between the moment someone started speaking and the silence that ended it.

    ``bytes_base64`` is raw little-endian PCM16 mono at ``sample_rate`` (the rate the microphone reports, after any
    resampling it was asked to do).
    """

    bytes_base64: str
    sample_rate: int


@dataclass(slots=True, frozen=True)
class MicrophoneUtteranceEvent(BaseEvent[MicrophoneUtteranceEventDTO]):
    type: Literal[EventType.UTTERANCE] = field(
        default=EventType.UTTERANCE,
        init=False,
    )
