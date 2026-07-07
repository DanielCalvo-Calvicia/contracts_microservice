from dataclasses import dataclass
from typing import Generic, TypeVar


from stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class StepperStreamStartedOutboundEventDTO:
    message: str

@dataclass(frozen=True, slots=True)
class StepperStreamStartedOutboundEvent(BaseEvent[StepperStreamStartedOutboundEventDTO]):
    type: str = "stream_started"