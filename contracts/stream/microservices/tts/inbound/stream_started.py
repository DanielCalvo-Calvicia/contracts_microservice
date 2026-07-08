from dataclasses import dataclass

from contracts.stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class TTSStreamStartedInboundEventDTO:
    pass

@dataclass(frozen=True, slots=True)
class TTSStreamStartedInboundEvent(BaseEvent[TTSStreamStartedInboundEventDTO]):
    type: str = "stream_started"