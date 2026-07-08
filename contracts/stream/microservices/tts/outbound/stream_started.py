from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class TTSStreamStartedOutboundEventDTO:
    pass

@dataclass(frozen=True, slots=True)
class TTSStreamStartedOutboundEvent(BaseEvent[TTSStreamStartedOutboundEventDTO]):
    type: str = "stream_started"