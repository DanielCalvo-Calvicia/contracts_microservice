from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class STTStreamStartedInboundEventDTO:
    """The PCM16 format of the audio that follows. STT rejects it if it differs from the format it was configured with."""

    sample_rate: int
    channels: int


@dataclass(frozen=True, slots=True)
class STTStreamStartedInboundEvent(BaseEvent[STTStreamStartedInboundEventDTO]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )
