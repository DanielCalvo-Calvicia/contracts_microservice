from dataclasses import dataclass, field
from typing import Literal


from contracts.stream.common.base import BaseEvent, EventType
    
@dataclass(slots=True, frozen=True)
class ErrorEventDTO:
    code: str
    message: str
    recoverable: bool

@dataclass(frozen=True, slots=True)
class ErrorEvent(BaseEvent[ErrorEventDTO]):
    type: Literal[EventType.ERROR] = field(
        default=EventType.ERROR,
        init=False,
    )