from dataclasses import dataclass
from typing import Generic, TypeVar


from stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class StepperStreamStartedInboundEventDTO:
    pass

@dataclass(frozen=True, slots=True)
class StepperStreamStartedInboundEvent(BaseEvent[StepperStreamStartedInboundEventDTO]):
    type: str = "stream_started"