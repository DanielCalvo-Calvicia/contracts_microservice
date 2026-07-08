from dataclasses import dataclass
from typing import Generic, TypeVar


from contracts.stream.common.base import BaseEvent
    
@dataclass(frozen=True, slots=True)
class HeartbeatEvent(BaseEvent[None]):
    type: str = "heartbeat"