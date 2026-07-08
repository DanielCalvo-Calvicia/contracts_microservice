from __future__ import annotations

from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent


@dataclass(slots=True, frozen=True)
class MicrophoneStreamStartedEventDTO:
    pass

@dataclass(slots=True, frozen=True)
class MicrophoneStreamStartedEvent(BaseEvent[MicrophoneStreamStartedEventDTO]):
    type: str = "stream_started"

