from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType
    
@dataclass(slots=True, frozen=True)
class MicrophoneStreamStartedEventDTO:
    message: str
    sample_rate: int
    channels: int

@dataclass(frozen=True, slots=True)
class MicrophoneStreamStartedEvent(BaseEvent[MicrophoneStreamStartedEventDTO]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )