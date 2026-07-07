from dataclasses import dataclass

from stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class STTStreamStartedInboundEventDTO:
    pass

@dataclass(frozen=True, slots=True)
class STTStreamStartedInboundEvent(BaseEvent[STTStreamStartedInboundEventDTO]):
    type: str = "stream_started"