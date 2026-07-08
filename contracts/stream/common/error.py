from dataclasses import dataclass
from typing import Generic, TypeVar


from contracts.stream.common.base import BaseEvent
    
@dataclass(slots=True, frozen=True)
class ErrorEventDTO:
    code: str
    message: str
    recoverable: bool

@dataclass(frozen=True, slots=True)
class ErrorEvent(BaseEvent[ErrorEventDTO]):
    type: str = "error"