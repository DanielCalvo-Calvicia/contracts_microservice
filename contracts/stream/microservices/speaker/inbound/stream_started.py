from dataclasses import dataclass
from typing import Generic, TypeVar


from contracts.stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class SpeakerStreamStartedInboundEventDTO:
    pass

@dataclass(frozen=True, slots=True)
class SpeakerStreamStartedInboundEvent(BaseEvent[SpeakerStreamStartedInboundEventDTO]):
    type: str = "stream_started"