from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class STTStreamStartedOutboundEventDTO:
    pass

@dataclass(frozen=True, slots=True)
class STTStreamStartedOutboundEvent(BaseEvent[STTStreamStartedOutboundEventDTO]):
    type: str = "stream_started"