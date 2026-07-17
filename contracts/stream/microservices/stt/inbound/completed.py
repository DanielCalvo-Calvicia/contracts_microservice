from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class STTCompletedInboundEventDTO:
    output_bytes_base64: str

@dataclass(slots=True, frozen=True)
class STTCompletedInboundEvent(BaseEvent[STTCompletedInboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

