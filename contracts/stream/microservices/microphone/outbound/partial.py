from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType



@dataclass(slots=True, frozen=True)
class MicrophonePartialEventDTO:
    bytes_base64: str


@dataclass(slots=True, frozen=True)
class MicrophonePartialEvent(BaseEvent[MicrophonePartialEventDTO]):
    type: Literal[EventType.PARTIAL] = field(
        default=EventType.PARTIAL,
        init=False,
    )