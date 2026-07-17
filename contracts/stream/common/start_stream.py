from dataclasses import dataclass
from typing import Literal
from dataclasses import field

from contracts.stream.common.base import BaseEvent, EventType
    
@dataclass(frozen=True, slots=True)
class StartStreamEvent(BaseEvent[None]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )