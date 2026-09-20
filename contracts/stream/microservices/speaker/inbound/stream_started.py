from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class SpeakerStreamStartedInboundEventDTO:
    """The PCM16 format of the audio that follows. The speaker rejects it if it differs from the format it was asked to play."""

    sample_rate: int
    channels: int


@dataclass(frozen=True, slots=True)
class SpeakerStreamStartedInboundEvent(BaseEvent[SpeakerStreamStartedInboundEventDTO]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )
