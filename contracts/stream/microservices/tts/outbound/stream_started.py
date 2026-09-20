from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from contracts.stream.common.base import BaseEvent, EventType


@dataclass(slots=True, frozen=True)
class TTSStreamStartedOutboundEventDTO:
    """The PCM16 format of every following ``partial``: the one requested when the text stream was set."""

    sample_rate: int
    channels: int


@dataclass(frozen=True, slots=True)
class TTSStreamStartedOutboundEvent(BaseEvent[TTSStreamStartedOutboundEventDTO]):
    type: Literal[EventType.START_STREAM] = field(
        default=EventType.START_STREAM,
        init=False,
    )
