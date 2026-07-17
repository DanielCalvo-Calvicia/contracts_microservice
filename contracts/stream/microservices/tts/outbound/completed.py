from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class CompletedOutboundEventDTO:
    reason: str
    output_bytes_base64: str
    total_bytes: int
    chunk_count: int

@dataclass(slots=True, frozen=True)
class CompletedOutboundEvent(BaseEvent[CompletedOutboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

