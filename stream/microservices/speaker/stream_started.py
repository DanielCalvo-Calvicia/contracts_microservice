from dataclasses import dataclass
from typing import Generic, TypeVar


from stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class MicrophoneStreamStartedEventDTO:
    message: str
    sample_rate: int
    channels: int

@dataclass(frozen=True, slots=True)
class MicrophoneStreamStartedEvent(BaseEvent[MicrophoneStreamStartedEventDTO]):
    type: str = "stream_started"