from dataclasses import dataclass
from typing import Generic, TypeVar


from contracts.stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class MicrophoneStreamStartedOutboundEventDTO:
    message: str

@dataclass(frozen=True, slots=True)
class MicrophoneStreamStartedOutboundEvent(BaseEvent[MicrophoneStreamStartedOutboundEventDTO]):
    type: str = "stream_started"