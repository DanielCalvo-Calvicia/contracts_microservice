from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class MicrophoneCompletedOutboundEventDTO:
    reason: str
    output_bytes_base64: str

@dataclass(slots=True, frozen=True)
class MicrophoneCompletedOutboundEvent(BaseEvent[MicrophoneCompletedOutboundEventDTO]):
    type: Literal[EventType.COMPLETED] = field(
        default=EventType.COMPLETED,
        init=False,
    )

