from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from dataclasses import field
from contracts.stream.common.base import BaseEvent, EventType

@dataclass(slots=True, frozen=True)
class PartialOutboundEventDTO:
    bytes_base64: str
    byte_count: int
    chunk_index: int


@dataclass(slots=True, frozen=True)
class PartialOutboundEvent(BaseEvent[PartialOutboundEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )